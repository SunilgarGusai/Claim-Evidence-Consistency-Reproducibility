# Frozen method protocol

## 1. Formal inputs

The reference implementation assumes a finite directed labeled **claim graph** `C`, finite directed labeled **evidence graph** `E`, candidate domain `D(u)` for every claim vertex, and relation-specific support/contradiction automata. Evidence arcs may carry reliability values and provenance identifiers.

The public computational package focuses on the algorithmic layer after these structured inputs exist. Natural-language claim extraction, entity linking, retrieval, source calibration, and relation/automaton construction are outside the formal guarantees.

## 2. Global alignment

An admissible alignment maps every claim vertex to one evidence vertex in its candidate domain. The same selected image must be reused across every incident claim relation. This global reuse condition distinguishes the model from independent claim-by-claim checking.

## 3. Support and contradiction semantics

For each relation label `r`, finite automata define support and contradiction languages over evidence-edge labels. The core theory uses **finite-walk semantics**. Product-graph reachability determines whether an accepted witness exists. Reliability-aware status uses the maximum bottleneck value among accepted walks (`widest accepted walk`) compared against relation thresholds.

## 4. Certificates

A positive certificate contains the alignment and one accepted provenance-bearing evidence walk for each claim arc whose support bottleneck reaches the required threshold. The verifier checks domains, endpoints, labels/automaton acceptance, threshold satisfaction, and provenance references independently of the search algorithm.

## 5. Structural algorithms

The public implementation contains:

- exhaustive alignment search for small-instance validation;
- binary arc-consistency pruning;
- exact dynamic programming on claim trees;
- exact dynamic programming for a supplied tree decomposition;
- exact specialization for a supplied feedback vertex set;
- exact min-sum correction on trees;
- exact and greedy source-cover certificate selection.

## 6. Frozen computational design

The submission-aligned design is encoded in `config/study_config.yaml` and uses fixed seed `20260712`.

- Tree exactness: `n={4,6,8,10}`, domain size 4, 25 instances each.
- Worst-case timing: `n={6,8,10,12,13}`, domain size 3, 5 instances each.
- Tree scalability: `n={50,200,1000,5000}`, domain sizes `{4,8,12}`, 8 instances per pair.
- FVS exactness: `n={5,7,9}`, domain size 3, supplied FVS size 1, 20 instances each.
- Weighted correction exactness: `n={4,6,8}`, domain size 3, 20 instances each.
- Evidence cover: universe sizes `{8,10,12,14,16,18}`, 30 instances each.

The experiments are algorithm-validation studies, not empirical claims about natural-language systems.
