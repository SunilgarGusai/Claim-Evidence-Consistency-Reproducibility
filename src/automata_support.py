from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from heapq import heappop, heappush
from typing import Dict, FrozenSet, Hashable, Mapping, Optional, Sequence, Set, Tuple
from .model import EvidenceGraph

State = Hashable

@dataclass(frozen=True)
class NFA:
    states: FrozenSet[State]
    alphabet: FrozenSet[str]
    start_states: FrozenSet[State]
    final_states: FrozenSet[State]
    transitions: Mapping[Tuple[State, str], FrozenSet[State]]

    @staticmethod
    def word(labels: Sequence[str]) -> 'NFA':
        states = frozenset(range(len(labels) + 1))
        transitions = {(i, a): frozenset({i + 1}) for i, a in enumerate(labels)}
        return NFA(states, frozenset(labels), frozenset({0}),
                   frozenset({len(labels)}), transitions)


def accepting_walk(graph: EvidenceGraph, nfa: NFA, source, target):
    """Return a shortest accepting product-graph path, or None."""
    adj = graph.adjacency()
    queue = deque()
    parent: Dict[Tuple[object, State], Optional[Tuple[object, State]]] = {}
    for q0 in nfa.start_states:
        z = (source, q0); queue.append(z); parent[z] = None
    final = None
    while queue:
        v, q = queue.popleft()
        if v == target and q in nfa.final_states:
            final = (v, q); break
        for label, nxt in adj.get(v, []):
            for q2 in nfa.transitions.get((q, label), frozenset()):
                z2 = (nxt, q2)
                if z2 not in parent:
                    parent[z2] = (v, q); queue.append(z2)
    if final is None:
        return None
    path = []
    cur = final
    while cur is not None:
        path.append(cur); cur = parent[cur]
    return tuple(reversed(path))


def _weighted_adjacency(graph: EvidenceGraph):
    out = {v: [] for v in graph.vertices}
    for arc in graph.arcs:
        u, label, v = arc
        out.setdefault(u, []).append((label, v, float(graph.reliability.get(arc, 1.0)), arc))
    return out


def widest_accepting_walk(graph: EvidenceGraph, nfa: NFA, source, target):
    """Return (bottleneck, product_path) for a strongest accepted walk.

    Product-path capacity is the minimum evidence reliability on the path.
    Ties are deterministic only up to heap ordering; the bottleneck value is exact.
    """
    adj = _weighted_adjacency(graph)
    best: Dict[Tuple[object, State], float] = {}
    parent: Dict[Tuple[object, State], Optional[Tuple[object, State]]] = {}
    heap = []
    counter = 0
    for q0 in nfa.start_states:
        z = (source, q0); best[z] = 1.0; parent[z] = None
        heappush(heap, (-1.0, counter, z)); counter += 1
    final = None
    while heap:
        negcap, _, (v, q) = heappop(heap)
        cap = -negcap
        if cap + 1e-15 < best[(v, q)]:
            continue
        if v == target and q in nfa.final_states:
            final = (v, q); break
        for label, nxt, reliability, arc in adj.get(v, []):
            for q2 in nfa.transitions.get((q, label), frozenset()):
                z2 = (nxt, q2); c2 = min(cap, reliability)
                if c2 > best.get(z2, -1.0) + 1e-15:
                    best[z2] = c2; parent[z2] = (v, q)
                    heappush(heap, (-c2, counter, z2)); counter += 1
    if final is None:
        return 0.0, None
    path = []
    cur = final
    while cur is not None:
        path.append(cur); cur = parent[cur]
    return best[final], tuple(reversed(path))


def accepted_pair(graph: EvidenceGraph, nfa: NFA, source, target) -> bool:
    return accepting_walk(graph, nfa, source, target) is not None


def relation_matrix(graph: EvidenceGraph, nfa: NFA, domain) -> Set[Tuple[object, object]]:
    return {(x, y) for x in domain for y in domain if accepted_pair(graph, nfa, x, y)}


def threshold_relation_matrix(graph: EvidenceGraph, nfa: NFA, domain, threshold: float):
    """Pairs connected by an accepted walk of bottleneck at least threshold."""
    result = set()
    for x in domain:
        for y in domain:
            strength, _ = widest_accepting_walk(graph, nfa, x, y)
            if strength + 1e-15 >= threshold:
                result.add((x, y))
    return result
