# Scientific claim boundaries

## Supported by the formal analysis

The study supports statements about:

- polynomial verification of a supplied alignment under the stated finite-walk semantics;
- NP-completeness of global claim–evidence consistency under the proved restrictions;
- exact algorithms for claim trees and supplied bounded-treewidth decompositions;
- the supplied-feedback-set specialization and its explicit dependence on cycle-set size and candidate-domain size;
- polynomial-size positive certificates under the model assumptions;
- deterministic reliability-perturbation stability for a fixed alignment with positive consistency margin;
- restricted hardness of minimum evidence certification;
- exact and harmonic-approximation algorithms for the source-cover abstraction;
- exact local weighted correction on structurally restricted claim graphs.

## Not established by this repository

The repository does not establish:

- accuracy of a particular LLM or hallucination detector;
- correctness of upstream claim extraction, entity linking, retrieval, NLI, or source-reliability estimation;
- calibrated probabilities from the reliability values;
- causal truth of evidence sources;
- tractability under simple-path, trail, temporal, source-disjoint, or connected-certificate semantics unless separately proved;
- FPT in feedback-vertex-set size alone when the candidate-domain size is unbounded.

## Interpretation of the reliability margin

The consistency margin is a deterministic sensitivity radius under the specified bottleneck reliability semantics. It is **not** a statistical confidence interval, posterior probability, or empirical calibration guarantee.

## Novelty boundary

Graph-structured evidence verification and claim–evidence graphs already exist in the literature. The study's novelty is attached to its formal definitions, proved complexity/tractability boundaries, provenance-bearing certificates, reliability-stability analysis, and coupled evidence/correction optimization problems—not to the mere use of graphs for fact verification.
