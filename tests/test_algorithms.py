from src.model import ClaimGraph, EvidenceGraph
from src.alignment import brute_force_alignment, is_consistent
from src.automata_support import NFA, accepting_walk, relation_matrix
from src.certificates import build_certificate, verify_certificate
from src.domain_pruning import arc_consistency
from src.tree_dp import tree_consistency, tree_min_cost
from src.treewidth_dp import solve_on_tree_decomposition
from src.evidence_cover import EvidenceItem, exact_cover_bitmask, greedy_cover


def test_tree_dp_matches_bruteforce():
    c=ClaimGraph((0,1,2),((0,'r',1),(1,'r',2)),{0:(0,1),1:(0,1),2:(0,1)})
    support={'r':{(0,1),(1,0)}}
    b=brute_force_alignment(c,support); d=tree_consistency(c,support)
    assert (b is None)==(d is None)
    assert d is None or is_consistent(c,d,support)


def test_inconsistent_constraint():
    c=ClaimGraph((0,1),((0,'r',1),),{0:(0,),1:(0,)})
    assert tree_consistency(c,{'r':set()}) is None


def test_cover_exact_and_greedy():
    items=[EvidenceItem('a',frozenset({0,1}),1),EvidenceItem('b',frozenset({1,2}),1),EvidenceItem('c',frozenset({2}),2)]
    opt,_=exact_cover_bitmask(3,items); gr,_=greedy_cover({0,1,2},items)
    assert opt==2 and gr>=opt


def test_tree_min_cost_deletes_arcs_independently():
    c=ClaimGraph((0,1),((0,'r',1),(1,'s',0)),{0:(0,),1:(1,)})
    local={(0,'r',1,0,1):1.0,(1,'s',0,1,0):10.0}
    deletion={(0,'r',1):5.0,(1,'s',0):2.0}
    cost,phi,deleted=tree_min_cost(c,local,deletion)
    assert cost==3.0 and phi=={0:0,1:1} and deleted==((1,'s',0),)


def test_product_automaton_witness_and_relation():
    e=EvidenceGraph(('x','z','y'),(('x','a','z'),('z','b','y')))
    nfa=NFA.word(('a','b'))
    path=accepting_walk(e,nfa,'x','y')
    assert path is not None and path[0][0]=='x' and path[-1][0]=='y'
    assert ('x','y') in relation_matrix(e,nfa,('x','y','z'))


def test_certificate_round_trip():
    c=ClaimGraph(('u','v'),(('u','r','v'),),{'u':('x',),'v':('y',)})
    e=EvidenceGraph(('x','z','y'),(('x','a','z'),('z','b','y')))
    automata={'r':NFA.word(('a','b'))}
    cert=build_certificate(c,e,{'u':'x','v':'y'},automata)
    assert verify_certificate(c,e,cert,automata)
    cert['alignment']['u']='y'
    assert not verify_certificate(c,e,cert,automata)


def test_arc_consistency_detects_empty_domain():
    c=ClaimGraph((0,1,2),((0,'r',1),(1,'r',2)),{0:(0,),1:(0,1),2:(1,)})
    support={'r':{(0,0)}}
    assert arc_consistency(c,support) is None


def test_arc_consistency_tree_nonempty_is_sufficient_here():
    c=ClaimGraph((0,1,2),((0,'r',1),(1,'r',2)),{0:(0,1),1:(0,1),2:(0,1)})
    support={'r':{(0,1),(1,0)}}
    pruned=arc_consistency(c,support)
    assert pruned is not None
    c2=ClaimGraph(c.vertices,c.arcs,pruned)
    assert tree_consistency(c2,support) is not None


def test_tree_decomposition_solver_matches_bruteforce_on_cycle():
    c=ClaimGraph((0,1,2,3),((0,'r',1),(1,'r',2),(2,'r',3),(3,'r',0)),
                 {i:(0,1,2) for i in range(4)})
    support={'r':{(x,y) for x in range(3) for y in range(3) if x!=y}}
    brute=brute_force_alignment(c,support)
    bags=[(0,1,2),(0,2,3)];edges=[(0,1)]
    td=solve_on_tree_decomposition(c,support,bags,edges)
    assert (brute is None)==(td is None)
    assert td is None or is_consistent(c,td,support)


def test_widest_accepting_walk_uses_strongest_bottleneck():
    from src.automata_support import widest_accepting_walk
    e=EvidenceGraph(
        ('x','a','b','y'),
        (('x','r','a'),('a','s','y'),('x','r','b'),('b','s','y')),
        reliability={('x','r','a'):0.9,('a','s','y'):0.4,
                     ('x','r','b'):0.7,('b','s','y'):0.7})
    nfa=NFA.word(('r','s'))
    strength,path=widest_accepting_walk(e,nfa,'x','y')
    assert abs(strength-0.7)<1e-12 and path is not None


def test_reliability_robustness_margin_bound():
    from src.automata_support import widest_accepting_walk
    from src.scoring import consistency_margin
    base=EvidenceGraph(('x','z','y'),(('x','a','z'),('z','b','y')),
                       reliability={('x','a','z'):0.86,('z','b','y'):0.82})
    pert=EvidenceGraph(('x','z','y'),(('x','a','z'),('z','b','y')),
                       reliability={('x','a','z'):0.83,('z','b','y'):0.79})
    nfa=NFA.word(('a','b'))
    s0,_=widest_accepting_walk(base,nfa,'x','y')
    s1,_=widest_accepting_walk(pert,nfa,'x','y')
    assert abs(s0-s1)<=0.03+1e-12
    margin=consistency_margin({'c':s0},{'c':0.10},{'c':0.75},{'c':0.50})
    assert margin>0.03 and s1>=0.75


def test_feedback_vertex_set_solver_matches_bruteforce_on_cycle():
    from src.fvs import solve_with_feedback_vertex_set
    c=ClaimGraph((0,1,2,3),((0,'r',1),(1,'r',2),(2,'r',3),(3,'r',0)),
                 {i:(0,1,2) for i in range(4)})
    support={'r':{(x,y) for x in range(3) for y in range(3) if x!=y}}
    brute=brute_force_alignment(c,support)
    fvs=solve_with_feedback_vertex_set(c,support,[0])
    assert (brute is None)==(fvs is None)
    assert fvs is None or is_consistent(c,fvs,support)
