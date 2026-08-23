# Struct3D Hypothesis Elimination Closure

## 1. Objective

The theory-facing Struct3D chain must not stop at externally supplied objects.
For one finite observation

`X = (x_0, ..., x_{n-1})`,

all load-bearing intermediate objects are now defined as deterministic
functions of `X`.

The closed dependency is

`X -> (A_max, Gamma, M, G_B, N_X, S_X, C_R, Phi_X)`

followed by

`Stage 2D -> Unit -> Relation -> World -> Representation`.

No semantic labels and no neural network are part of this construction.

## 2. Observation-derived objects

### A_max(X)

`A_max(X) = Pi(Omega_X)` where `Omega_X = {0,...,n-1}` and `Pi` is the
complete finite set-partition lattice.

Thus `A_max(X)` is finite and non-empty for every non-empty finite `X`.

### Gamma(X)

The frozen default is

`Gamma(X) = A_max(X)`.

Therefore Gamma is automatically a finite, non-empty, complete candidate
family and is closed under observation-index relabeling.

### M(X)

`M(X)` is the deterministic finite family of point, line, and plane models
fitted to `X`. Model residuals are functions of the observed coordinates only.

### G_B(X)

`G_B(X)` is the complete finite pairwise observation graph with

`w_ij = 1 / (1 + ||x_i-x_j|| / diam(X))`.

For non-singleton observations all weights are strictly positive and the total
weight is positive.

### N_X and S_X

`N_X(u)` is the finite insertion/deletion neighborhood on the observation
index universe. `S_X(u)` is the finite family of all non-empty proper support
subsets of `u`.

### C_R(X)

For a materialized world with `m` Units,

`C_R(X) = {(i,j): 0 <= i,j < m, i != j}`.

Relation formation therefore has no externally supplied candidate pair list.
The current observation-derived relation rule is normalized minimum
cross-support Euclidean distance, with explicit evidence and confidence.

### Phi_X

`Phi_X(W)` is the deterministic 23-dimensional representation computed from
`X`, the materialized Units, and the X-derived Relations. It is not an
externally supplied extractor on the canonical path.

## 3. Canonical implementation interface

`ObservationDerivedContext.from_points(X)` is the single provenance carrier.
It exposes:

- `a_max`, `gamma`
- `model_family`
- `boundary_graph`
- `unit_candidates`
- `neighborhood_rule(u)`
- `proper_subcandidates(u)`
- `relation_candidates(m)`
- `materialize_partitions()`
- `stage2d_energy()`
- `form_relations(units)`
- `build_world(partition)`
- `phi_x(world)`

This prevents the canonical pipeline from silently replacing one boundary
with an independently supplied object.

## 4. Closure status

The former external boundaries are no longer mathematical assumptions in the
canonical finite-observation execution path. They are observation-derived
constructive objects.

The remaining distinction is important: the low-level compatibility APIs
still accept explicit objects for regression and historical use. Those APIs
are not the canonical theorem path and must not be used as evidence that the
observation-derived theorem has been proved.

The canonical path is therefore provenance-closed at the engineering level:

`X -> A_max/Gamma -> M/G_B/N_X/S_X/C_R -> Stage2D -> Unit -> Relation -> W -> Phi_X`.

Regression tests in `tests/test_hypothesis_elimination.py` enforce this
provenance contract.
