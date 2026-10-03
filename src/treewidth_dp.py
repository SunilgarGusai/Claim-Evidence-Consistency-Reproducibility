from __future__ import annotations
from collections import defaultdict, deque
from itertools import product
from typing import Dict, Iterable, Mapping, Optional, Sequence, Set, Tuple
from .model import ClaimGraph

Compatibility = Mapping[str, Set[Tuple[object, object]]]


def _is_pair_consistent(claim, phi, support, contradiction, vertices):
    contradiction = contradiction or {}
    vset = set(vertices)
    for u, relation, v in claim.arcs:
        if u in vset and v in vset:
            pair = (phi[u], phi[v])
            if pair not in support.get(relation, set()):
                return False
            if pair in contradiction.get(relation, set()):
                return False
    return True


def validate_tree_decomposition(claim: ClaimGraph, bags: Sequence[Sequence[object]], tree_edges):
    """Validate coverage and running-intersection properties."""
    if not bags:
        raise ValueError('At least one bag is required.')
    bag_sets = [set(b) for b in bags]
    all_vertices = set().union(*bag_sets)
    if all_vertices != set(claim.vertices):
        raise ValueError('Tree-decomposition bags do not cover exactly the claim vertices.')
    edge_set = {frozenset(e) for e in tree_edges}
    if len(edge_set) != len(bags) - 1:
        raise ValueError('Bag graph must contain |bags|-1 distinct edges.')
    adj = {i: set() for i in range(len(bags))}
    for e in edge_set:
        if len(e) != 2:
            raise ValueError('Invalid bag-tree edge.')
        i, j = tuple(e)
        if i not in adj or j not in adj:
            raise ValueError('Bag-tree edge references an unknown bag.')
        adj[i].add(j); adj[j].add(i)
    seen = set(); q = deque([0])
    while q:
        i = q.popleft()
        if i in seen: continue
        seen.add(i); q.extend(adj[i] - seen)
    if len(seen) != len(bags):
        raise ValueError('Bag graph is not a tree.')
    for u, _, v in claim.arcs:
        if not any(u in b and v in b for b in bag_sets):
            raise ValueError('A claim constraint is not covered by any bag.')
    for vertex in claim.vertices:
        nodes = {i for i, b in enumerate(bag_sets) if vertex in b}
        start = next(iter(nodes)); reached = set(); q = deque([start])
        while q:
            i = q.popleft()
            if i in reached or i not in nodes: continue
            reached.add(i); q.extend(adj[i])
        if reached != nodes:
            raise ValueError('Running-intersection property is violated.')
    return adj, bag_sets


def solve_on_tree_decomposition(
    claim: ClaimGraph,
    support: Compatibility,
    bags: Sequence[Sequence[object]],
    tree_edges: Iterable[Tuple[int, int]],
    contradiction: Optional[Compatibility] = None,
    root: int = 0,
):
    """Solve CEC on a supplied tree decomposition using junction-tree DP."""
    claim.validate()
    adj, bag_sets = validate_tree_decomposition(claim, bags, tree_edges)
    parent = {root: None}; order = []; q = deque([root])
    while q:
        i = q.popleft(); order.append(i)
        for j in adj[i]:
            if j not in parent:
                parent[j] = i; q.append(j)
    children = {i: [] for i in range(len(bags))}
    for j, p in parent.items():
        if p is not None: children[p].append(j)

    ordered_bags = [tuple(b) for b in bags]
    assignments = {}
    feasible = {}
    choices = {}
    for i, bag in enumerate(ordered_bags):
        vals = []
        for images in product(*(claim.domains[u] for u in bag)):
            phi = dict(zip(bag, images))
            if _is_pair_consistent(claim, phi, support, contradiction, bag):
                vals.append(images)
        assignments[i] = vals

    for i in reversed(order):
        bag = ordered_bags[i]
        feasible[i] = set()
        for assn in assignments[i]:
            phi = dict(zip(bag, assn)); ok = True
            for j in children[i]:
                child_bag = ordered_bags[j]
                intersection = tuple(u for u in child_bag if u in bag_sets[i])
                matching = []
                for child_assn in feasible[j]:
                    child_phi = dict(zip(child_bag, child_assn))
                    if all(phi[u] == child_phi[u] for u in intersection):
                        matching.append(child_assn)
                if not matching:
                    ok = False; break
                choices[(i, assn, j)] = matching[0]
            if ok:
                feasible[i].add(assn)
    if not feasible[root]:
        return None

    root_assn = next(iter(feasible[root]))
    solution = {}
    stack = [(root, root_assn)]
    while stack:
        i, assn = stack.pop()
        solution.update(dict(zip(ordered_bags[i], assn)))
        for j in children[i]:
            stack.append((j, choices[(i, assn, j)]))
    return solution
