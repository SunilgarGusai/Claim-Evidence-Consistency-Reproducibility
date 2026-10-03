from __future__ import annotations
from itertools import product
from typing import Mapping, Optional, Sequence, Set, Tuple

from .model import ClaimGraph
from .tree_dp import tree_consistency

Compatibility = Mapping[str, Set[Tuple[object, object]]]


def _arc_ok(u, r, v, xu, xv, support, contradiction):
    if (xu, xv) not in support.get(r, set()):
        return False
    if contradiction and (xu, xv) in contradiction.get(r, set()):
        return False
    return True


def solve_with_feedback_vertex_set(
    claim: ClaimGraph,
    support: Compatibility,
    feedback_vertices: Sequence[object],
    contradiction: Optional[Compatibility] = None,
):
    """Solve CEC given a feedback vertex set of the underlying claim graph.

    The supplied feedback_vertices must be such that deleting them leaves a forest.
    The algorithm enumerates their candidate images, filters the remaining domains,
    and solves each residual tree exactly.
    """
    claim.validate()
    contradiction = contradiction or {}
    X = tuple(dict.fromkeys(feedback_vertices))
    xset = set(X)
    if not xset.issubset(set(claim.vertices)):
        raise ValueError('Feedback vertex set contains an unknown claim vertex.')

    remaining = tuple(u for u in claim.vertices if u not in xset)

    adj = {u: set() for u in remaining}
    for u, _, v in claim.arcs:
        if u in adj and v in adj and u != v:
            adj[u].add(v); adj[v].add(u)
    seen = set()
    for start in remaining:
        if start in seen:
            continue
        parent = {start: None}
        stack = [start]
        while stack:
            u = stack.pop(); seen.add(u)
            for v in adj[u]:
                if v == parent[u]:
                    continue
                if v in parent:
                    raise ValueError('Deleting the supplied vertices does not leave a forest.')
                parent[v] = u; stack.append(v)

    for images in product(*(claim.domains[u] for u in X)):
        alpha = dict(zip(X, images))
        ok = True
        for u, r, v in claim.arcs:
            if u in xset and v in xset:
                if not _arc_ok(u, r, v, alpha[u], alpha[v], support, contradiction):
                    ok = False; break
        if not ok:
            continue

        reduced = {}
        for u in remaining:
            vals = []
            for yu in claim.domains[u]:
                good = True
                for a, r, b in claim.arcs:
                    if a == u and b in xset:
                        if not _arc_ok(a, r, b, yu, alpha[b], support, contradiction):
                            good = False; break
                    if b == u and a in xset:
                        if not _arc_ok(a, r, b, alpha[a], yu, support, contradiction):
                            good = False; break
                if good:
                    vals.append(yu)
            if not vals:
                ok = False; break
            reduced[u] = tuple(vals)
        if not ok:
            continue

        solution = dict(alpha)
        component_seen = set()
        for start in remaining:
            if start in component_seen:
                continue
            comp = []
            stack = [start]; component_seen.add(start)
            while stack:
                u = stack.pop(); comp.append(u)
                for v in adj[u]:
                    if v not in component_seen:
                        component_seen.add(v); stack.append(v)
            cset = set(comp)
            comp_arcs = tuple(a for a in claim.arcs if a[0] in cset and a[2] in cset)
            sub = ClaimGraph(tuple(comp), comp_arcs, {u: reduced[u] for u in comp},
                             {a: claim.weights.get(a, 1.0) for a in comp_arcs})
            phi = tree_consistency(sub, support, contradiction, root=start)
            if phi is None:
                ok = False; break
            solution.update(phi)
        if ok:
            return solution
    return None
