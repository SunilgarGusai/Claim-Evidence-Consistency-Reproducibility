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
    evidence_edges = {tuple(a[:3]) for a in evidence.arcs}
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


def build_full_certificate(claim: ClaimGraph, evidence: EvidenceGraph, phi,
                           support_automata, contradiction_automata,
                           support_thresholds, contradiction_thresholds):
    """Strict CEC certificate including provenance and reliability."""
    from .automata_support import widest_accepting_walk
    if set(phi) != set(claim.vertices) or any(phi[u] not in claim.domains[u] for u in claim.vertices):
        raise ValueError("Invalid candidate-constrained alignment")
    _require_edge_metadata(evidence)
    entries = []
    for index,(u,relation,v) in enumerate(claim.arcs):
        if any(relation not in m for m in (support_automata, contradiction_automata,
                                          support_thresholds, contradiction_thresholds)):
            raise ValueError("Missing automata or thresholds")
        plus=float(support_thresholds[relation]); minus=float(contradiction_thresholds[relation])
        if not (0 < plus <= 1 and 0 < minus <= 1):
            raise ValueError("Thresholds must lie in (0,1]")
        strength,path=widest_accepting_walk(evidence,support_automata[relation],phi[u],phi[v])
        conflict,_=widest_accepting_walk(evidence,contradiction_automata[relation],phi[u],phi[v])
        if path is None or strength < plus or conflict >= minus:
            raise ValueError("The alignment has no contradiction-free positive certificate")
        used=[]
        for (x,q),(y,next_q) in zip(path,path[1:]):
            arcs=[a for a in evidence.arcs if a[0]==x and a[2]==y
                  and next_q in support_automata[relation].transitions.get((q,a[1]),frozenset())
                  and evidence.reliability[a] >= strength - 1e-12]
            if not arcs:
                raise ValueError("Product path does not match reliable evidence arcs")
            a=max(arcs,key=lambda e:evidence.reliability[e])
            used.append({"edge":list(a),"provenance":evidence.provenance[a],
                         "reliability":float(evidence.reliability[a])})
        entries.append({"index":index,"claim_arc":[u,relation,v],
                        "product_path":[list(state) for state in path],"edges":used})
    return {"alignment":dict(phi),"entries":entries}


def _require_edge_metadata(evidence: EvidenceGraph):
    if any(a not in evidence.reliability or a not in evidence.provenance
           or not isinstance(evidence.provenance[a],str) or not evidence.provenance[a].strip()
           or not 0 <= float(evidence.reliability[a]) <= 1 for a in evidence.arcs):
        raise ValueError("Full semantics require explicit provenance and reliability on every evidence arc")


def verify_full_certificate(claim: ClaimGraph, evidence: EvidenceGraph,
                            certificate, support_automata, contradiction_automata,
                            support_thresholds, contradiction_thresholds) -> bool:
    """Verify positive path, provenance, reliability, and contradiction absence.

    Unlike the legacy path-only helper, this checks the full manuscript semantics.
    Absence of contradiction is checked by polynomial widest accepted walks.
    """
    from .automata_support import widest_accepting_walk
    try:
        _require_edge_metadata(evidence)
        phi=certificate["alignment"]; entries=certificate["entries"]
        if set(phi) != set(claim.vertices) or len(entries) != len(claim.arcs):
            return False
        if any(phi[u] not in claim.domains[u] for u in claim.vertices):
            return False
        for index,((u,relation,v), entry) in enumerate(zip(claim.arcs,entries)):
            if entry["index"] != index or entry["claim_arc"] != [u,relation,v]:
                return False
            if any(relation not in m for m in (support_automata,contradiction_automata,
                                               support_thresholds,contradiction_thresholds)):
                return False
            plus=float(support_thresholds[relation]);minus=float(contradiction_thresholds[relation])
            if not (0 < plus <= 1 and 0 < minus <= 1):
                return False
            path=[tuple(x) for x in entry["product_path"]]
            if not path or path[0][0]!=phi[u] or path[-1][0]!=phi[v]:
                return False
            automaton=support_automata[relation]
            if path[0][1] not in automaton.start_states or path[-1][1] not in automaton.final_states:
                return False
            edges=entry["edges"]
            if len(edges) != len(path)-1:
                return False
            bottleneck=1.0
            for (x,q),(y,q2),record in zip(path,path[1:],edges):
                arc=tuple(record["edge"])
                if len(arc) not in (3,4) or arc not in evidence.arcs or arc[0]!=x or arc[2]!=y:
                    return False
                if q2 not in automaton.transitions.get((q,arc[1]),frozenset()):
                    return False
                if record["provenance"] != evidence.provenance[arc]:
                    return False
                rho=float(evidence.reliability[arc])
                if abs(float(record["reliability"])-rho)>1e-12:
                    return False
                bottleneck=min(bottleneck,rho)
            if bottleneck<plus:
                return False
            contrad,_=widest_accepting_walk(evidence,contradiction_automata[relation],phi[u],phi[v])
            if contrad>=minus:
                return False
        return True
    except (KeyError,ValueError,TypeError,IndexError,AttributeError):
        return False
