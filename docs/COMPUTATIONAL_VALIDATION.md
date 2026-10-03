# Computational validation

The computational section checks reference implementations against exhaustive comparators on deliberately small instances, then records seeded scaling behavior for structurally tractable regimes.

## Exactness comparisons

- Tree CEC: 100 generated instances, exhaustive search versus tree DP.
- Supplied FVS: 60 generated cyclic instances with `|X|=1`, exhaustive search versus FVS specialization.
- Weighted correction: 60 generated tree instances, exhaustive assignment optimization versus min-sum tree DP.

## Scaling experiment

Tree instances use claim sizes up to 5,000 and domain sizes up to 12. These runs illustrate implementation scaling; wall-clock measurements are hardware-dependent.

## Evidence cover

180 generated source-cover instances compare the polynomial greedy heuristic with exact bitmask optimization. The numerical ratio distribution is illustrative; the theoretical harmonic guarantee is independent of these runs.

## Re-running

Use `python scripts/reproduce_validation.py`. Fresh outputs are placed in `results/reproduced/` so the committed `results/frozen/` snapshot is not overwritten accidentally.
