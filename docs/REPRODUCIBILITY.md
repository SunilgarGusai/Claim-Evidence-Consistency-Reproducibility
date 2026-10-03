# Reproducibility boundary

## Public reviewer-facing layer

The `main` branch contains the reference algorithms, tests, deterministic experiment generator, frozen machine-readable results, environment specifications, example inputs, documentation, and figure-regeneration utilities needed to inspect and validate the computational component of the study.

## Frozen submission layer

The intended `v1.0.0-submission` GitHub release should preserve the exact public computational snapshot associated with the submitted manuscript. Reviewers should use the frozen release when they need an immutable reference rather than the live branch.

## Intentionally excluded during peer review

The public repository does **not** mirror:

- submitted manuscript PDF;
- LaTeX manuscript source / journal class bundle;
- cover letter;
- graphical-abstract journal submission file;
- author photographs;
- Editorial Manager forms or correspondence.

This separation prevents the public reproducibility artifact from becoming a duplicate journal-submission package.

## Reproduction levels

1. `pytest -q` checks reference implementations and invariants.
2. `python scripts/validate_public_artifact.py` validates the curated repository and frozen results.
3. `python scripts/reproduce_validation.py` regenerates the deterministic computational validation into `results/reproduced/`.
4. `python scripts/generate_figures.py` regenerates reviewer-facing scientific figures from the public plotting functions/results.

Runtime values vary with hardware. Agreement/exactness outcomes and seeded generated-instance logic are the intended reproducible claims.
