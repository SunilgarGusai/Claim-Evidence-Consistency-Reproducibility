from __future__ import annotations
from dataclasses import dataclass
from math import inf
from typing import Iterable, List, Sequence, Set, Tuple

@dataclass(frozen=True)
class EvidenceItem:
    name: str
    covers: frozenset[int]
    cost: float = 1.0


def greedy_cover(universe: Set[int], items: Sequence[EvidenceItem]):
    uncovered = set(universe); chosen=[]; total=0.0
    while uncovered:
        candidates=[]
        for item in items:
            gain = len(item.covers & uncovered)
            if gain: candidates.append((item.cost/gain, item.name, item))
        if not candidates:
            return inf, tuple()
        _, _, best = min(candidates)
        chosen.append(best); total += best.cost
        uncovered -= best.covers
    return total, tuple(chosen)


def exact_cover_bitmask(m: int, items: Sequence[EvidenceItem]):
    full=(1<<m)-1
    dp=[inf]*(1<<m); parent=[None]*(1<<m); dp[0]=0.0
    masks=[]
    for item in items:
        mask=0
        for x in item.covers:
            if 0 <= x < m: mask |= 1<<x
        masks.append(mask)
    for i,(item,imask) in enumerate(zip(items,masks)):
        old=dp[:]
        for mask,c in enumerate(old):
            if c==inf: continue
            nm=mask|imask; nc=c+item.cost
            if nc < dp[nm]-1e-12:
                dp[nm]=nc; parent[nm]=(mask,i)
    if dp[full]==inf: return inf, tuple()
    chosen=[]; cur=full
    while cur:
        prev,i=parent[cur]; chosen.append(items[i]); cur=prev
    chosen.reverse()
    return dp[full], tuple(chosen)
