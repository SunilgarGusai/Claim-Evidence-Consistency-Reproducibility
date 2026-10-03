from __future__ import annotations
from typing import Mapping
from .automata_support import NFA, accepting_walk
from .model import ClaimGraph, EvidenceGraph


def build_certificate(claim: ClaimGraph, evidence: EvidenceGraph,
                      phi: Mapping[object, object],
                      support_automata: Mapping[str, NFA]):
    witnesses = {}
    for a in claim.arcs:
        u, relation, v = a
        path = accepting_walk(evidence, support_automata[relation], phi[u], phi[v])
        if path is None:
            raise ValueError(f'No support witness for {a!r}.')
        witnesses[repr(a)] = [[node, state] for node, state in path]
    return {'alignment': dict(phi), 'witnesses': witnesses}


def verify_certificate(claim: ClaimGraph, evidence: EvidenceGraph,
                       certificate, support_automata: Mapping[str, NFA]) -> bool:
    """Independently verify alignment domains and stored product-graph paths."""
    phi = certificate.get('alignment', {})
    if set(phi) != set(claim.vertices):
        return False
    if any(phi[u] not in claim.domains[u] for u in claim.vertices):
        return False
    evidence_edges = {(u, label, v) for u, label, v in evidence.arcs}
    for a in claim.arcs:
        u, relation, v = a
        raw = certificate.get('witnesses', {}).get(repr(a))
        if not raw:
            return False
        path = [tuple(z) for z in raw]
        if path[0][0] != phi[u] or path[-1][0] != phi[v]:
            return False
        nfa = support_automata[relation]
        if path[0][1] not in nfa.start_states or path[-1][1] not in nfa.final_states:
            return False
        for (x, q), (y, q2) in zip(path, path[1:]):
            valid = False
            for e_u, label, e_v in evidence_edges:
                if e_u == x and e_v == y and q2 in nfa.transitions.get((q, label), frozenset()):
                    valid = True; break
            if not valid:
                return False
    return True
