from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Hashable, Iterable, List, Mapping, Sequence, Set, Tuple

Node = Hashable
ClaimArc = Tuple[Node, str, Node]
EvidenceArc = Tuple[Node, str, Node]

@dataclass(frozen=True)
class ClaimGraph:
    vertices: Tuple[Node, ...]
    arcs: Tuple[ClaimArc, ...]
    domains: Mapping[Node, Tuple[Node, ...]]
    weights: Mapping[ClaimArc, float] = field(default_factory=dict)

    def validate(self) -> None:
        vset = set(self.vertices)
        for u, _, v in self.arcs:
            if u not in vset or v not in vset:
                raise ValueError('Every claim-arc endpoint must be a claim vertex.')
        for u in self.vertices:
            if u not in self.domains or not self.domains[u]:
                raise ValueError(f'Candidate domain is empty or missing for {u!r}.')

@dataclass(frozen=True)
class EvidenceGraph:
    vertices: Tuple[Node, ...]
    arcs: Tuple[EvidenceArc, ...]
    reliability: Mapping[EvidenceArc, float] = field(default_factory=dict)
    provenance: Mapping[EvidenceArc, str] = field(default_factory=dict)

    def adjacency(self) -> Dict[Node, List[Tuple[str, Node]]]:
        out: Dict[Node, List[Tuple[str, Node]]] = {v: [] for v in self.vertices}
        for u, label, v in self.arcs:
            out.setdefault(u, []).append((label, v))
        return out
