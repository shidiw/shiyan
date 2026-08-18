# Struct3D Theory-Compliant Refactor — Audit 1

## Baseline

- Base branch: `main`
- Baseline commit: `239f04cddbbd560777409de28b46d3e5400fc1f0`
- Refactor branch: `refactor/theory-compliant-core`

This document records what is currently implemented versus what is formally justified. It is a refactor control document, not a new mathematical theory.

## Rule

A code path may enter the theory-compliant core only when its mathematical definition is already established in the Struct3D theory specification. Engineering heuristics remain available as legacy code and must not be silently promoted to theory.

## Energy → Partition → Unit audit

### 1. Energy (`structure/energy.py`)

The current implementation computes

`E = E_fit + lambda * E_complexity + gamma * E_boundary`.

Observed implementation facts:

- Plane fitting uses mean squared signed-plane residual after taking absolute distance.
- Sphere fitting uses mean squared radial residual.
- Cylinder fitting uses an XY-only radial residual around an axis-aligned cylinder center.
- Complexity is a lookup table: plane=4, sphere=4, cylinder=5, unknown=10.
- Boundary is the variance of point-to-centroid Euclidean distances.
- Default weights are `lambda_complexity=0.01` and `gamma_boundary=0.01`.
- `compute()` stores the total on `unit.energy` and returns all four components.

Theory classification:

- `E_fit`: **candidate geometric residual implementation**. It is not yet a universal definition of the Struct3D energy unless the theory specification explicitly fixes these primitive families and residual measures.
- `E_complexity`: **legacy heuristic**. Parameter-count/dimension lookup is not promoted to a mathematical complexity functional.
- `E_boundary`: **legacy heuristic**. The source itself calls this a first version and describes later graph-boundary replacement.
- `lambda`, `gamma`: **legacy engineering hyperparameters**.
- The additive decomposition: **legacy implementation structure only**; it is not an axiom in this refactor.

Status: **LEGACY / FROZEN FOR REGRESSION ONLY**.

### 2. Partition (`structure/graph_cluster.py`)

The current implementation:

1. Takes a structural graph `G=(V,E,W)`.
2. Keeps edges satisfying `w >= threshold`.
3. Builds connected components.
4. Removes components with fewer than `min_points` points.
5. Converts each retained component into a `StructuralUnit` with `primitive="unknown"`.

Default values are `threshold=0.5` and `min_points=50`.

Theory classification:

- Thresholding is an engineering rule.
- Connected components are an algorithmic consequence of that rule, not yet the formal Stable Partition definition.
- `min_points` is an engineering filter.
- No energy minimization is performed here.

Therefore the current module cannot be represented as

`Pi* = argmin_Pi E(Pi)`

without adding mathematical assumptions that are not present in the code or verified by this audit.

Status: **LEGACY / FROZEN FOR REGRESSION ONLY**.

### 3. Structural Unit (`structure/unit.py`)

The current container is represented as

`U_k = (P_k, theta_k, E_k)`.

The implementation stores points, a primitive label, optional point indices, parameters, and energy. It also provides candidate parameter estimation for plane, sphere, and an axis-aligned cylinder.

Important implementation limitations:

- Primitive support is finite and hard-coded.
- Cylinder fitting is axis-aligned and therefore is not a general 3D cylinder estimator.
- Parameter fitting is not tied to a formal admissible class or a proven minimizer of a Struct3D objective.
- The unit container does not itself establish uniqueness, stability, or optimality.

Status: **LEGACY / CANDIDATE IMPLEMENTATION**.

## Regression suite added

New files:

- `tests/__init__.py`
- `tests/test_legacy_energy_unit.py`

The suite characterizes historical behavior without declaring that behavior to be theory. It covers:

- default Energy hyperparameters;
- exact plane/sphere/cylinder fit residuals;
- legacy complexity lookup;
- legacy centroid-radius boundary variance;
- `Energy.compute()` output and mutation behavior;
- graph-cluster threshold and minimum-size behavior;
- connected-component extraction into units;
- minimum-size filtering;
- StructuralUnit container, center, indices, and initial energy state;
- plane parameter estimation;
- unknown primitive behavior.

The tests use Python's standard `unittest` framework and therefore do not introduce a new testing dependency.

### Execution note

The regression suite has been committed to the refactor branch, but this environment cannot resolve `github.com` for a local clone, so the tests could not be executed here. No test result is being claimed without execution. The suite is intended to be run from the repository root with:

`python -m unittest discover -s tests -v`

## Required formal boundary

The core refactor must eventually expose the following separation:

`candidate partition -> formally defined structural objective -> admissible minimization/stability rule -> Structural Unit`

The exact objective and admissible class must come from the established Struct3D theory. No new terms, weights, thresholds, or relation types are introduced by this audit.

## Next gate

Before changing Energy or Partition implementation, recover/verify the exact established mathematical definitions for:

1. admissible structural primitives;
2. structural fitting functional;
3. complexity term, if any;
4. boundary term, if any;
5. whether the total objective is additive or has another aggregation law;
6. admissible partition class;
7. definition of stable partition;
8. definition of Structural Unit and whether its parameters are minimizers, estimators, or descriptors.

Only after those items are verified should a theory-facing implementation replace or wrap the legacy modules.

## Prohibited during this refactor

- Inventing a new energy term.
- Treating an engineering threshold as a mathematical constant.
- Treating a connected-component heuristic as a theorem.
- Replacing historical code before regression behavior is captured.
- Changing `main`.
