# Quick start

This is the public reproducibility companion for the claim–evidence consistency study.

If you only want to understand the study, read in this order:

1. `README.md`
2. `docs/METHOD_PROTOCOL.md`
3. `docs/FROZEN_RESULTS.md`
4. `docs/CLAIM_BOUNDARIES.md`

## 1. Create the environment

### Conda

```bash
conda env create -f environment.yml
conda activate claim-evidence-tcs
```

### Or pip / venv

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 2. Run the 12 reference tests

```bash
pytest -q
```

Expected submission-aligned outcome: `12 passed`.

## 3. Validate the curated public artifact

```bash
python scripts/validate_public_artifact.py
```

This checks repository structure, manifest coverage, exclusion of journal-private files, frozen numerical invariants, seed/configuration consistency, and the principal validation counts.

## 4. Reproduce the deterministic computational validation

```bash
python scripts/reproduce_validation.py
```

Fresh outputs are written to `results/reproduced/`. Runtime measurements are hardware-dependent; logical outcomes and seeded generated instances are deterministic under the pinned environment.

## 5. Regenerate reviewer-facing figures

```bash
python scripts/generate_figures.py
```

Generated PDF/SVG/PNG figures are written to `figures/`. The committed scientific repository visuals in `docs/assets/` are also reproducible from the same plotting functions.

## 6. Follow formal claims to code and evidence

Use:

```text
docs/FROZEN_RESULTS.md
REPOSITORY_MANIFEST.csv
results/frozen/
```

## Important interpretation notes

- The experiments validate theorem implementations and boundary cases; they are not an LLM-accuracy benchmark.
- Walk semantics, candidate domains, automata, reliability values, and thresholds are explicit inputs to the formal layer.
- Reliability-stability margins are deterministic robustness radii, not statistical confidence intervals.
- Submission manuscript files are intentionally not mirrored in the public repository during peer review.
