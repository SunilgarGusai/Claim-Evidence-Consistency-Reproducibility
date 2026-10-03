from __future__ import annotations
from collections import defaultdict, deque
from math import inf
from typing import Dict, Iterable, List, Mapping, Optional, Set, Tuple
from .model import ClaimGraph

Compatibility = Mapping[str, Set[Tuple[object, object]]]


def _tree_structure(claim: ClaimGraph, root=None):
    vertices = list(claim.vertices)
    if not vertices:
        return None, {}, {}, []
    root = vertices[0] if root is None else root
    und = {u: set() for u in vertices}
    by_pair = defaultdict(list)
    for a in claim.arcs:
        u, r, v = a
        und[u].add(v); und[v].add(u)
        by_pair[frozenset((u, v))].append(a)
    parent = {root: None}
    order = []
    q = deque([root])
    while q:
        u = q.popleft(); order.append(u)
        for v in und[u]:
            if v not in parent:
                parent[v] = u; q.append(v)
            elif parent[u] != v:
                raise ValueError('The underlying claim graph is not a tree.')
    if len(parent) != len(vertices) or sum(len(x) for x in und.values()) // 2 != len(vertices)-1:
        raise ValueError('The underlying claim graph is not a tree.')
    children = {u: [] for u in vertices}
    for v, p in parent.items():
        if p is not None: children[p].append(v)
    return root, parent, children, order, by_pair


def _pair_ok(arcs, x, y, parent, child, support, contradiction):
    contradiction = contradiction or {}
    for u, r, v in arcs:
        pair = (x, y) if (u, v) == (parent, child) else (y, x)
        if pair not in support.get(r, set()) or pair in contradiction.get(r, set()):
            return False
    return True


def tree_consistency(claim: ClaimGraph, support: Compatibility,
                     contradiction: Optional[Compatibility] = None,
                     root=None):
    root, parent, children, order, by_pair = _tree_structure(claim, root)
    if root is None: return {}
    feasible: Dict[object, Dict[object, bool]] = {}
    choice: Dict[Tuple[object, object, object], object] = {}
    for u in reversed(order):
        feasible[u] = {}
        for x in claim.domains[u]:
            ok = True
            for v in children[u]:
                candidates = [y for y in claim.domains[v]
                              if feasible[v].get(y, False)
                              and _pair_ok(by_pair[frozenset((u,v))], x, y, u, v,
                                           support, contradiction)]
                if not candidates:
                    ok = False; break
                choice[(u, x, v)] = candidates[0]
            feasible[u][x] = ok
    roots = [x for x in claim.domains[root] if feasible[root].get(x, False)]
    if not roots: return None
    phi = {root: roots[0]}
    stack = [root]
    while stack:
        u = stack.pop()
        for v in children[u]:
            phi[v] = choice[(u, phi[u], v)]
            stack.append(v)
    return phi


def tree_min_cost(claim: ClaimGraph,
                  local_cost: Mapping[Tuple[object,str,object,object,object], float],
                  deletion_cost: Optional[Mapping[Tuple[object,str,object], float]] = None,
                  root=None):
    """Minimum local inconsistency/deletion cost on a claim tree.

    local_cost[(u,r,v,x,y)] is the cost of keeping arc (u,r,v) when
    endpoints map to x,y. deletion_cost permits dropping an arc.
    """
    root, parent, children, order, by_pair = _tree_structure(claim, root)
    deletion_cost = deletion_cost or {}
    dp: Dict[object, Dict[object, float]] = {}
    choice = {}
    for u in reversed(order):
        dp[u] = {}
        for x in claim.domains[u]:
            total = 0.0
            for v in children[u]:
                best = inf; best_y = None; best_deleted = ()
                arcs = by_pair[frozenset((u,v))]
                for y in claim.domains[v]:
                    cand = dp[v][y]
                    deleted_here = []
                    for a in arcs:
                        a_u, r, a_v = a
                        if (a_u, a_v) == (u, v):
                            keep_cost = local_cost.get((a_u, r, a_v, x, y), inf)
                        else:
                            keep_cost = local_cost.get((a_u, r, a_v, y, x), inf)
                        drop_cost = deletion_cost.get(a, inf)
                        if drop_cost < keep_cost:
                            cand += drop_cost
                            deleted_here.append(a)
                        else:
                            cand += keep_cost
                    if cand < best:
                        best, best_y, best_deleted = cand, y, tuple(deleted_here)
                total += best
                choice[(u,x,v)] = (best_y,best_deleted)
            dp[u][x] = total
    x0 = min(claim.domains[root], key=lambda x: dp[root][x])
    phi = {root:x0}; deleted=[]; stack=[root]
    while stack:
        u=stack.pop()
        for v in children[u]:
            y, deleted_here = choice[(u,phi[u],v)]
            phi[v]=y
            deleted.extend(deleted_here)
            stack.append(v)
    return dp[root][x0], phi, tuple(deleted)
