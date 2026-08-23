# Struct3D Global Mathematical Closure Audit

Branch: `refactor/theory-compliant-core`

## 1. Audit rule

The preserved `Struct3D_数学理论.txt` remains authoritative for recovered
historical theory. Newly derived closure stages are explicitly labeled as
extensions and are required to have a mathematical definition, implementation
contract, and regression test.

## 2. Final upstream verdict

`X -> ObservationDerivedTheoryInterface -> A(X) -> A_max(X) -> Gamma(X) -> E_X -> Stable -> MinimalStable -> Unit -> Relation -> Graph -> World -> Canonical Form -> Invariant -> phi -> D_R -> Matching -> Neural`

The release-facing theorem boundary is now frozen as
`ObservationDerivedTheoryInterface`, concretely implemented by
`ObservationDerivedBoundaries.from_points(X)`. The constructor accepts only
`X`; former external boundaries cannot be injected independently.

| Link | Verdict | Reason |
|---|---|---|
| `X -> A(X)` | **CLOSED FINITELY AS DERIVED EXTENSION** | `A_max(X)=Pi(Omega_X)` is the complete finite partition lattice and `Gamma(X)=A_max(X)`. |
| `A(X) -> P*` | **CLOSED CONDITIONALLY** | Finite, non-empty candidate family plus finite energy gives an attained argmin. |
| `E` | **DERIVED EXTENSION** | Stage 2D supplies a normalized finite-observation functional. It is a mathematically explicit extension, not a historical recovery. |
| `P* -> Stable` | **CLOSED CONDITIONALLY** | A global minimizer is locally stable for every explicitly supplied neighborhood; the observation-derived path now supplies `N_X`. |
| `Stable -> MinimalStable` | **CLOSED AS DERIVED EXTENSION** | The observation-derived path supplies `S_X` as all non-empty proper support subsets. |
| `MinimalStable -> Unit` | **CLOSED AS DERIVED EXTENSION** | Materialization uses the frozen StructuralUnit type after the observation-derived predicates pass. |
| `Unit -> Relation` | **CLOSED AS DERIVED EXTENSION** | `C_R(X)` is all ordered Unit pairs and the closed path supplies observation-derived proximity evidence. |
| `Relation -> Graph` | **CLOSED** | Graph edges are copied from the relation set. |
| `Graph -> World` | **CLOSED** | `W=(U,R,Phi)` is implemented as a validated container. |
| `World -> Canonical` | **CLOSED FOR FINITE REGIME** | Exhaustive finite relabeling canonicalization is exact for the declared validation regime. |
| `Canonical -> Invariant` | **CLOSED** | Frozen choice `I(W)=C(W)`. |
| `Invariant -> phi in R^23` | **CLOSED AS COORDINATE MAP** | `Phi_X(W)` is explicitly defined from X and W; quotient well-definedness is regression-tested. Injectivity is not claimed. |
| `phi -> D_R` | **CLOSED** | Exact Euclidean representation-space distance. |
| `D_R -> Matching` | **CLOSED GENERICALLY** | Explicit finite/admissible correspondence set and supplied cost are minimized. |
| `phi -> neural latent metric` | **OPEN** | Reconstruction or empirical correlation does not prove latent metric equality. |

## 3. Exact observation-derived definitions

### 3.1 Candidate family

For `X=(x_0,...,x_{n-1})`, let `Omega_X={0,...,n-1}`.

`A_max(X)=Pi(Omega_X)` and `Gamma(X)=A_max(X)`.

Thus `Gamma(X)` is finite, non-empty, and invariant under every permutation of
observation indices.

### 3.2 Model family

`M(X)` is the finite family of three canonical affine fits to X:

`{point(X), line(X), plane(X)}`.

The point model is centered at the observation centroid. The line uses the
largest coordinate variance axis and the plane uses the smallest coordinate
variance axis. Complexity is `0,1,2` respectively. No semantic label is used.

### 3.3 Boundary graph

`G_B(X)` is the complete graph on `Omega_X` with

`w_ij = 1/(1+||x_i-x_j||/diam(X))`.

For `n>1`, every weight is positive and total weight is positive. The singleton
case is the unique zero-boundary case retained by the Stage 2D contract.

### 3.4 Stability and minimality domains

`N_X(S)` consists of supports obtained from S by adding or deleting exactly one
observation index, with S itself used only as the neutral singleton case.

`S_X(S)` is the family of all non-empty proper subsets of S.

Both are finite and permutation-compatible.

### 3.5 Relation candidate domain

For a world with k X-derived Units,

`C_R(X)={(i,j):0<=i,j<k, i!=j}`.

The current closed relation path assigns every candidate pair a `proximity`
relation whose evidence is the normalized minimum cross-support Euclidean
distance and confidence `1/(1+d_norm)`. The stronger H^2 boundary-contact
predicate remains a separate optional relation theorem.

### 3.6 Representation

`Phi_X(W)` is a fixed 23-dimensional map consisting of:

1. affine-model-type histogram;
2. singleton/intermediate/full-support composition histogram;
3. Unit-count/non-singleton/component topology statistics;
4. relation-type histogram;
5. relation confidence min/mean/max;
6. Unit occupancy min/mean/max;
7. five global structural counts.

Every coordinate is finite for a valid finite observation/world. The coordinate
map is Unit-label invariant, hence well-defined on the finite quotient.
Injectivity and semantic completeness are not claimed.

## 4. Frozen formal interface

The formal theorem boundary is implemented in
`structure/theory_observation_interface.py` as
`ObservationDerivedTheoryInterface`. The concrete release facade is
`structure/theory_closed_form.py::ObservationDerivedBoundaries`.

The interface freezes these members as read-only derived projections:

`X, A_max, Gamma, M, G_B, N_X, S_X, C_R, Phi_X, energy, world, representation`.

No constructor argument exists for any former external boundary. Passing an
independent `A_max`, `M`, `G_B`, `N_X`, `S_X`, `C_R`, or `Phi_X` is therefore a
contract violation. The regression test
`test_observation_derived_formal_interface.py` protects this boundary.

## 5. Energy and historical regression boundary

The Stage 2D functional remains a **DERIVED EXTENSION**. It is a mathematically
explicit extension, not a historical recovery. The legacy `structure/energy.py` remains regression-only and is not part of the observation-derived proof path.

The observation-derived constructor now consumes `M(X)` and `G_B(X)` directly.
The Stage 2D separation margin remains a verified property of a finite family,
not a circular additive term in the energy.

## 6. Relation boundary interpretation

The generic Stage 3 relation theorem still has the form

`R_Q = { r_ij : (i,j) in C_R, Q(i,j)=True }`.

The observation-derived path closes `C_R(X)` and supplies a concrete proximity
relation. The stronger universal relation claim is intentionally not silently
promoted. The audit marker **Universal relation construction** therefore remains
explicitly qualified as a research-level theorem question.

## 7. What is now closed and what is not

The formerly external construction boundaries are no longer external in the
observation-derived execution path: `A(X)`, `M(X)`, `G_B(X)`, `N_X/S_X`, and
`C_R(X)` are generated by `ObservationDerivedContext`; `Phi_X` is generated by
`represent_observation`/`phi_x`. The formal interface now freezes those
projections as the single theorem-facing API.

The old explicit-input APIs remain low-level compatibility interfaces. They are
not the proof path for the closed observation-derived pipeline.

The remaining genuinely open research claims are:

1. semantic adequacy of the derived energy;
2. injectivity/information completeness of the 23-D `Phi_X` map;
3. **Universal relation construction** as a canonical law;
4. Object/Instance/Hierarchy definitions and theorems;
5. Neural distance preservation.

The neural item remains open: **Neural distance preservation** is not implied by
reconstruction.

## 8. Engineering regression markers retained

The engineering audit records that Stage 2D rejects `NaN` **and** positive/negative infinity,
rejects negative observation indices, rejects duplicate ordered edges, and
requires finite real values at the theory-facing boundaries. These are
implementation contracts, not mathematical semantics.

## 9. Release interpretation

A passing regression suite establishes implementation-contract consistency.
The observation-derived path now removes hidden external construction
assumptions from the upstream pipeline, and the formal interface freezes the
remaining theorem boundary. It does not turn derived definitions into recovered
historical theory or prove semantic correctness.

The closed mathematical engineering path is:

`X -> A_max/Gamma -> M(X),G_B(X),N_X,S_X,C_R(X) -> E_X -> Unit -> Relation -> World -> Phi_X -> D_R`.
