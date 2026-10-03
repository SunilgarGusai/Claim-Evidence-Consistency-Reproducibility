# Frozen result inventory

This document maps the submission-aligned computational statements to committed machine-readable files.

## Exactness

| Validation block | Frozen outcome | Source |
|---|---:|---|
| Tree consistency | 100 / 100 decisions agree with exhaustive search | `results/frozen/tree_validation.csv` |
| Supplied-FVS consistency | 60 / 60 decisions agree with exhaustive search | `results/frozen/fvs_validation.csv` |
| Weighted tree correction | 60 / 60 optima agree with exhaustive optimization | `results/frozen/correction_validation.csv` |
| Largest correction discrepancy | < 9 × 10^-16 | `results/frozen/correction_validation.csv` |
| Reference unit tests | 12 / 12 pass | `tests/test_algorithms.py` |

## Scalability

Tree consistency was evaluated up to **5,000 claim vertices** at candidate-domain sizes 4, 8, and 12. The frozen median timings are hardware-specific and should not be treated as portable performance guarantees; the committed CSV exists to document the exact submission-side run.

Source: `results/frozen/tree_scalability.csv`.

## Evidence-cover experiment

For each universe size `m ∈ {8,10,12,14,16,18}`, 30 deterministic generated instances compare greedy cover cost against the exact bitmask optimum, for **180 total instances**.

Source: `results/frozen/cover_results.csv`.

The experiment illustrates finite-instance behavior; the theoretical guarantee is the standard harmonic-factor bound proved for the source-cover abstraction.

## Seed and summary

- Seed: `20260712`
- Consolidated summary: `results/frozen/summary.json`
- Frozen design: `config/study_config.yaml`

## Result-to-code map

| Result | Implementation |
|---|---|
| Product/widest witness | `src/automata_support.py` |
| Arc consistency | `src/domain_pruning.py` |
| Tree exactness / correction | `src/tree_dp.py` |
| Bounded treewidth | `src/treewidth_dp.py` |
| Feedback vertex set | `src/fvs.py` |
| Evidence cover | `src/evidence_cover.py` |
| Certificate verification | `src/certificates.py` |
| Experiment generation | `src/experiments.py` |
