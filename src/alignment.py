from __future__ import annotations
from itertools import product
from typing import Dict, Mapping, Optional, Set, Tuple
from .model import ClaimGraph

Compatibility = Mapping[str, Set[Tuple[object, object]]]


def is_consistent(claim: ClaimGraph, phi: Mapping[object, object],
                  support: Compatibility,
                  contradiction: Optional[Compatibility] = None) -> bool:
    contradiction = contradiction or {}
    for u, r, v in claim.arcs:
        pair = (phi[u], phi[v])
        if pair not in support.get(r, set()):
            return False
        if pair in contradiction.get(r, set()):
            return False
    return True


def brute_force_alignment(claim: ClaimGraph, support: Compatibility,
                          contradiction: Optional[Compatibility] = None):
    claim.validate()
    domains = [claim.domains[u] for u in claim.vertices]
    for values in product(*domains):
        phi = dict(zip(claim.vertices, values))
        if is_consistent(claim, phi, support, contradiction):
            return phi
    return None
