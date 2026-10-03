from __future__ import annotations
from typing import Mapping, Optional, Set, Tuple
from .model import ClaimGraph


def inconsistency_score(claim: ClaimGraph, phi: Mapping[object,object],
                        support: Mapping[str,Set[Tuple[object,object]]],
                        contradiction: Optional[Mapping[str,Set[Tuple[object,object]]]]=None,
                        unsupported_penalty: float=1.0,
                        contradiction_penalty: float=2.0) -> float:
    contradiction = contradiction or {}
    score=0.0
    for a in claim.arcs:
        u,r,v=a; pair=(phi[u],phi[v]); w=claim.weights.get(a,1.0)
        if pair not in support.get(r,set()): score += unsupported_penalty*w
        if pair in contradiction.get(r,set()): score += contradiction_penalty*w
    return score


def consistency_margin(support_strengths, contradiction_strengths,
                       support_thresholds, contradiction_thresholds):
    """Minimum signed reliability margin of a supplied alignment.

    Inputs are mappings keyed by the same claim-arc identifiers. Positive return
    values certify robustness to any uniform edge-reliability perturbation smaller
    than the returned margin (with graph structure and automata fixed).
    """
    margins=[]
    for a in support_strengths:
        margins.append(float(support_strengths[a])-float(support_thresholds[a]))
        margins.append(float(contradiction_thresholds[a])-float(contradiction_strengths[a]))
    return min(margins) if margins else float('inf')
