# Struct3D Theory-Compliant Refactor — Audit 0

## Baseline

- Base branch: `main`
- Baseline commit: `239f04cddbbd560777409de28b46d3e5400fc1f0`
- Refactor branch: `refactor/theory-compliant-core`

This document records what is currently implemented versus what is formally justified. It is a refactor control document, not a new mathematical theory.

## Rule

A code path may enter the theory-compliant core only when its mathematical definition is already established in the Struct3D theory specification. Engineering heuristics remain available as legacy code and must not be silently promoted to theory.

## Layer 1 — Structural Unit

Current file: `structure/unit.py`.

Implemented representation:

`U_k = (P_k, theta_k, E_k)`

This is a data representation, not by itself a proof of a unique or optimal unit. Primitive fitting currently supports plane, sphere, and an axis-aligned cylinder. Therefore the fitting routines are classified as **engineering implementations of candidate parameter estimation**, not as universal definitions of Structural Unit.

Status: **LEGACY / CANDIDATE IMPLEMENTATION**.

## Layer 2 — Energy

Current file: `structure/energy.py`.

Implemented expression:

`E = E_fit + lambda * E_complexity + gamma * E_boundary`

The current implementation defines complexity using primitive parameter dimension and defines boundary using variance of point-to-centroid distances. The source itself describes the latter as a first version and says it was later intended to be replaced by graph boundary.

Therefore:

- `E_fit`: candidate geometric residual implementation.
- `E_complexity`: engineering heuristic unless explicitly present in the theory specification.
- `E_boundary`: engineering heuristic in the current implementation.
- `lambda`, `gamma`: engineering hyperparameters in the current implementation.
- The additive decomposition itself is **not promoted to an axiom** by this refactor.

Status: **LEGACY / FROZEN FOR REGRESSION ONLY**.

## Layer 3 — Graph Cluster / Unit Extraction

Current file: `structure/graph_cluster.py`.

The implementation constructs connected components after thresholding graph weights by `threshold=0.5`, then drops components smaller than `min_points=50`.

These values are engineering choices. Connected-component extraction after thresholding is therefore not yet accepted as the formal definition of Stable Partition.

Status: **LEGACY / FROZEN FOR REGRESSION ONLY**.

## Required formal boundary

The core refactor must eventually expose the following separation:

`candidate partition -> formally defined structural objective -> admissible minimization/stability rule -> Structural Unit`

The exact objective and admissible class must come from the established Struct3D theory. No new terms, weights, thresholds, or relation types are introduced by this audit.

## Immediate next implementation step

1. Preserve current `energy.py`, `graph_cluster.py`, and `unit.py` as legacy behavior.
2. Add tests that characterize their current behavior so historical results remain reproducible.
3. Create theory-facing interfaces only after the corresponding mathematical definitions are recovered/verified.
4. Then audit Relation and Assembly against those definitions.

## Prohibited during this refactor

- Inventing a new energy term.
- Treating an engineering threshold as a mathematical constant.
- Treating a connected-component heuristic as a theorem.
- Replacing historical code before regression behavior is captured.
- Changing `main`.
