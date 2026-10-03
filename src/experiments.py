from __future__ import annotations
import argparse, csv, json, random, statistics, time
from itertools import product
from math import inf
from pathlib import Path
import networkx as nx
from .model import ClaimGraph
from .alignment import brute_force_alignment
from .domain_pruning import arc_consistency
from .tree_dp import tree_consistency, tree_min_cost
from .evidence_cover import EvidenceItem, exact_cover_bitmask, greedy_cover
from .fvs import solve_with_feedback_vertex_set

SEED = 20260712

def random_tree_instance(n: int, d: int, rng: random.Random, density: float = 0.36):
    tree = nx.random_labeled_tree(n, seed=rng.randrange(1 << 30))
    vertices = tuple(range(n)); arcs = []
    for u, v in tree.edges():
        arcs.append((u, 'r', v) if rng.random() < 0.5 else (v, 'r', u))
    domains = {u: tuple(range(d)) for u in vertices}
    support = {(x, y) for x in range(d) for y in range(d) if rng.random() < density}
    if not support: support.add((0, 0))
    return ClaimGraph(vertices, tuple(arcs), domains), {'r': support}

def random_fvs1_instance(n: int, d: int, rng: random.Random, density: float = 0.42):
    if n < 4: raise ValueError('n must be at least 4')
    tree = nx.random_labeled_tree(n - 1, seed=rng.randrange(1 << 30))
    arcs = []
    for a, b in tree.edges():
        u, v = a + 1, b + 1
        arcs.append((u, 'r', v) if rng.random() < 0.5 else (v, 'r', u))
    attach = rng.sample(list(range(1, n)), k=min(3, n - 1))
    for v in attach:
        arcs.append((0, 'r', v) if rng.random() < 0.5 else (v, 'r', 0))
    domains = {u: tuple(range(d)) for u in range(n)}
    support = {(x, y) for x in range(d) for y in range(d) if rng.random() < density}
    if not support: support.add((0, 0))
    return ClaimGraph(tuple(range(n)), tuple(arcs), domains), {'r': support}

def ensure_cover(m: int, k: int, rng: random.Random):
    items = []
    for j in range(k):
        cov = {i for i in range(m) if rng.random() < 0.28}
        items.append(EvidenceItem(f'e{j}', frozenset(cov), round(rng.uniform(0.5, 3.0), 3)))
    covered = set().union(*(x.covers for x in items)) if items else set()
    for i in range(m):
        if i not in covered:
            j = rng.randrange(k); old = items[j]
            items[j] = EvidenceItem(old.name, frozenset(set(old.covers) | {i}), old.cost)
    return items

def random_correction_instance(n: int, d: int, rng: random.Random):
    claim, _ = random_tree_instance(n, d, rng, density=0.5)
    local = {}; deletion = {}
    for a in claim.arcs:
        u, relation, v = a
        deletion[a] = round(rng.uniform(0.7, 2.8), 4)
        for x in claim.domains[u]:
            for y in claim.domains[v]:
                local[(u, relation, v, x, y)] = round(rng.uniform(0.0, 4.5), 4)
    return claim, local, deletion

def brute_force_min_cost(claim, local, deletion):
    best = inf
    for images in product(*(claim.domains[u] for u in claim.vertices)):
        phi = dict(zip(claim.vertices, images)); cost = 0.0
        for a in claim.arcs:
            u, relation, v = a
            keep = local[(u, relation, v, phi[u], phi[v])]
            cost += min(keep, deletion[a])
        best = min(best, cost)
    return best

def median(values):
    return statistics.median(values)

def run(outdir: Path):
    rng = random.Random(SEED); outdir.mkdir(parents=True, exist_ok=True)
    tree_rows = []
    for n in [4,6,8,10]:
        for rep in range(25):
            claim, support = random_tree_instance(n, 4, rng)
            t0=time.perf_counter(); brute=brute_force_alignment(claim,support); tb=time.perf_counter()-t0
            t0=time.perf_counter(); dp=tree_consistency(claim,support); td=time.perf_counter()-t0
            tree_rows.append({'n':n,'rep':rep,'bruteforce_s':tb,'tree_dp_s':td,'consistent':int(brute is not None),'agreement':int((brute is None)==(dp is None))})
    with (outdir/'tree_validation.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=tree_rows[0].keys()); w.writeheader(); w.writerows(tree_rows)

    worst_rows=[]
    for n in [6,8,10,12,13]:
        vertices=tuple(range(n)); arcs=tuple((i,'r',i+1) for i in range(n-1))
        claim=ClaimGraph(vertices,arcs,{u:(0,1,2) for u in vertices}); support={'r':set()}
        for rep in range(5):
            t0=time.perf_counter(); brute_force_alignment(claim,support); tb=time.perf_counter()-t0
            t0=time.perf_counter(); tree_consistency(claim,support); td=time.perf_counter()-t0
            worst_rows.append({'n':n,'rep':rep,'bruteforce_s':tb,'tree_dp_s':td})
    with (outdir/'worst_case_timing.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=worst_rows[0].keys()); w.writeheader(); w.writerows(worst_rows)

    scalability_rows=[]
    for d in [4,8,12]:
        for n in [50,200,1000,5000]:
            for rep in range(8):
                claim,support=random_tree_instance(n,d,rng,density=max(0.10,1.7/d))
                initial=sum(len(claim.domains[u]) for u in claim.vertices)
                pruned=arc_consistency(claim,support)
                t0=time.perf_counter(); result=tree_consistency(claim,support); td=time.perf_counter()-t0
                remaining=0 if pruned is None else sum(len(pruned[u]) for u in claim.vertices)
                scalability_rows.append({'n':n,'d':d,'rep':rep,'tree_dp_s':td,'consistent':int(result is not None),'pruned_fraction':(initial-remaining)/initial})
    with (outdir/'tree_scalability.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=scalability_rows[0].keys()); w.writeheader(); w.writerows(scalability_rows)

    fvs_rows=[]
    for n in [5,7,9]:
        for rep in range(20):
            claim,support=random_fvs1_instance(n,3,rng)
            t0=time.perf_counter(); brute=brute_force_alignment(claim,support); tb=time.perf_counter()-t0
            t0=time.perf_counter(); sol=solve_with_feedback_vertex_set(claim,support,[0]); tf=time.perf_counter()-t0
            fvs_rows.append({'n':n,'rep':rep,'bruteforce_s':tb,'fvs_s':tf,'agreement':int((brute is None)==(sol is None))})
    with (outdir/'fvs_validation.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fvs_rows[0].keys()); w.writeheader(); w.writerows(fvs_rows)

    correction_rows=[]
    for n in [4,6,8]:
        for rep in range(20):
            claim,local,deletion=random_correction_instance(n,3,rng)
            exact=brute_force_min_cost(claim,local,deletion); dp,_,_=tree_min_cost(claim,local,deletion)
            correction_rows.append({'n':n,'rep':rep,'exact':exact,'tree_dp':dp,'abs_error':abs(exact-dp)})
    with (outdir/'correction_validation.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=correction_rows[0].keys()); w.writeheader(); w.writerows(correction_rows)

    cover_rows=[]
    for m in [8,10,12,14,16,18]:
        for rep in range(30):
            items=ensure_cover(m,min(26,m+7),rng)
            opt,_=exact_cover_bitmask(m,items); greedy,_=greedy_cover(set(range(m)),items)
            cover_rows.append({'m':m,'rep':rep,'opt_cost':opt,'greedy_cost':greedy,'ratio':greedy/opt})
    with (outdir/'cover_results.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cover_rows[0].keys()); w.writeheader(); w.writerows(cover_rows)

    summary={'seed':SEED,'tree_validation':{},'worst_case':{},'scalability':{},'fvs_validation':{},'correction_validation':{},'cover':{}}
    for n in [4,6,8,10]:
        rows=[r for r in tree_rows if r['n']==n]
        summary['tree_validation'][str(n)]={'instances':len(rows),'consistent_fraction':sum(r['consistent'] for r in rows)/len(rows),'agreement':sum(r['agreement'] for r in rows)/len(rows),'median_bruteforce_ms':1000*median([r['bruteforce_s'] for r in rows]),'median_tree_dp_ms':1000*median([r['tree_dp_s'] for r in rows])}
    for n in [6,8,10,12,13]:
        rows=[r for r in worst_rows if r['n']==n]
        summary['worst_case'][str(n)]={'instances':len(rows),'median_bruteforce_ms':1000*median([r['bruteforce_s'] for r in rows]),'median_tree_dp_ms':1000*median([r['tree_dp_s'] for r in rows])}
    for d in [4,8,12]:
        for n in [50,200,1000,5000]:
            rows=[r for r in scalability_rows if r['n']==n and r['d']==d]
            summary['scalability'][f'{n}-{d}']={'instances':len(rows),'median_dp_ms':1000*median([r['tree_dp_s'] for r in rows]),'median_pruned_fraction':median([r['pruned_fraction'] for r in rows]),'consistent_fraction':sum(r['consistent'] for r in rows)/len(rows)}
    for n in [5,7,9]:
        rows=[r for r in fvs_rows if r['n']==n]
        summary['fvs_validation'][str(n)]={'instances':len(rows),'agreement':sum(r['agreement'] for r in rows)/len(rows),'median_bruteforce_ms':1000*median([r['bruteforce_s'] for r in rows]),'median_fvs_ms':1000*median([r['fvs_s'] for r in rows])}
    for n in [4,6,8]:
        rows=[r for r in correction_rows if r['n']==n]
        summary['correction_validation'][str(n)]={'instances':len(rows),'max_abs_error':max(r['abs_error'] for r in rows),'mean_abs_error':sum(r['abs_error'] for r in rows)/len(rows)}
    for m in [8,10,12,14,16,18]:
        rows=[r for r in cover_rows if r['m']==m]; ratios=sorted(r['ratio'] for r in rows)
        summary['cover'][str(m)]={'instances':len(rows),'mean_ratio':sum(ratios)/len(ratios),'median_ratio':median(ratios),'p95_ratio':ratios[max(0,int(.95*len(ratios))-1)],'max_ratio':max(ratios)}
    (outdir/'summary.json').write_text(json.dumps(summary,indent=2))
    return summary

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='results/frozen')
    args=ap.parse_args(); print(json.dumps(run(Path(args.out)), indent=2))
