from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Hashable, Iterable, List, Mapping, Sequence, Set, Tuple

Node = Hashable
ClaimArc = Tuple[Node, str, Node]
EvidenceArc = Tuple[Node, str, Node] | Tuple[Node, str, Node, Hashable]

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

    def __post_init__(self) -> None:
        # A four-tuple (source, label, target, arc_id) distinguishes parallel
        # statements with the same endpoints and label but different provenance.
        if any(len(a) not in (3, 4) for a in self.arcs):
            raise ValueError('Evidence arcs must have three or four fields.')
        if len(set(self.arcs)) != len(self.arcs):
            raise ValueError('Identical evidence-arc keys require distinct arc IDs.')
        if any(a[0] not in self.vertices or a[2] not in self.vertices
               for a in self.arcs):
            raise ValueError('Evidence arcs must have valid endpoints.')

    def adjacency(self) -> Dict[Node, List[Tuple[str, Node]]]:
        out: Dict[Node, List[Tuple[str, Node]]] = {v: [] for v in self.vertices}
        for a in self.arcs:
            u, label, v = a[:3]
            out.setdefault(u, []).append((label, v))
        return out
