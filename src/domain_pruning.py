from __future__ import annotations
from collections import defaultdict, deque
from typing import Dict, Mapping, Optional, Set, Tuple
from .model import ClaimGraph

Compatibility = Mapping[str, Set[Tuple[object, object]]]


def _pair_ok(arcs, x, y, u, v, support, contradiction):
    contradiction = contradiction or {}
    for a_u, relation, a_v in arcs:
        pair = (x, y) if (a_u, a_v) == (u, v) else (y, x)
        if pair not in support.get(relation, set()):
            return False
        if pair in contradiction.get(relation, set()):
            return False
    return True


def arc_consistency(
    claim: ClaimGraph,
    support: Compatibility,
    contradiction: Optional[Compatibility] = None,
):
    """Enforce binary arc consistency on candidate domains.

    Returns a dict of pruned tuple domains, or None when a domain becomes empty.
    Multiple/opposite claim arcs between the same endpoints are conjoined.
    """
    claim.validate()
    domains: Dict[object, Set[object]] = {u: set(claim.domains[u]) for u in claim.vertices}
    by_pair = defaultdict(list)
    neighbors = {u: set() for u in claim.vertices}
    for a in claim.arcs:
        u, _, v = a
        by_pair[frozenset((u, v))].append(a)
        neighbors[u].add(v)
        neighbors[v].add(u)

    queue = deque((u, v) for u in claim.vertices for v in neighbors[u])
    while queue:
        u, v = queue.popleft()
        arcs = by_pair[frozenset((u, v))]
        removed = {
            x for x in domains[u]
            if not any(_pair_ok(arcs, x, y, u, v, support, contradiction)
                       for y in domains[v])
        }
        if removed:
            domains[u] -= removed
            if not domains[u]:
                return None
            for z in neighbors[u] - {v}:
                queue.append((z, u))
    return {u: tuple(sorted(values, key=repr)) for u, values in domains.items()}
