# Struct3D mathematics → engineering-code contract

This document is the release gate for the `refactor/theory-compliant-core` branch.
The mathematical theory is authoritative. Historical engineering descriptions
are evidence, not automatic definitions.

## A. Observation-derived closure map

| Boundary | Observation-derived definition | Engineering location | Status |
|---|---|---|---|
| `A_max(X)` | complete finite partition lattice `Pi(Omega_X)` | `structure/theory_candidates.py` | **Implemented** |
| `Gamma(X)` | frozen candidate family, currently `A_max(X)` | `structure/theory_candidates.py` | **Implemented** |
| `M(X)` | three canonical affine model fits: point, line, plane | `structure/theory_observation.py` | **Frozen** by Model Universe Theorem |
| `G_B(X)` | complete weighted observation graph with `w_ij=1/(1+d_ij/diam(X))` | `structure/theory_observation.py` | **Frozen** by Boundary-Regularization Graph Theorem |
| `N_X` | one-index insertion/deletion neighborhood on Unit supports | `structure/theory_observation.py` | **Implemented** |
| `S_X` | all non-empty proper support subsets | `structure/theory_observation.py` | **Implemented** |
| `C_R(X)` | all ordered pairs of distinct materialized Units | `structure/theory_observation.py` | **Implemented** |
| `Q_X` | finite normalized cross-support distance has positive confidence | `structure/theory_relation_formation.py` | **Frozen** by Observation-Derived Relation Predicate Theorem |
| `Phi_X` | fixed 23-D finite structural statistics of `(X,W)` | `structure/theory_representation.py` | **Implemented coordinate map** |
| Stage 2D `E_X` | canonical energy consuming `M(X)` and `G_B(X)` with frozen weights `(1,1)` | `structure/theory_energy_model.py` | **Frozen observation-derived constructor** |
| `delta_X` | minimum positive quotient-distinct energy gap in `Gamma(X)` | `structure/theory_energy_model.py` | **Derived, never externally supplied** |
| Stage 2E | consumes `N_X`, `S_X`, and Unit competitors from `X` | `structure/theory_unit_formation.py` | **Observation-derived constructor implemented** |
| Unit → Relation | consumes `C_R(X)` and frozen `Q_X` with observation-derived evidence | `structure/theory_relation_formation.py` | **Frozen observation path** |
| Relation → World | copies derived relations into `W=(U,R,Phi)` | `structure/theory_pipeline.py`, `structure/theory_world.py` | **Implemented** |
| World → Representation | `Phi_X(W)` | `structure/theory_representation.py` | **Implemented** |

## B. Preserved frozen objects

- Structural Unit: `u=(G,theta)`.
- Explicit Relation: `r=(source,target,type,evidence)`.
- Structural Graph: `G=(V,E)` with edges copied from the relation set.
- Structural World: `W=(U,R,Phi)`.
- Canonical form: exact finite `C(W)`.
- Structural invariant: `I(W)=C(W)`.
- Representation distance: `D_R=||Phi_X(W1)-Phi_X(W2)||_2`.
- Finite/admissible matching and Stage 2F/2G conditional theorems remain valid.

## C. Mathematical contracts of the new closure

### 1. Finite candidate domain

For a finite observation index universe `Omega_X={0,...,n-1}`,

`A_max(X)=Pi(Omega_X)`

is finite and non-empty. `Gamma(X)=A_max(X)` is therefore also finite,
non-empty, and invariant under every permutation of observation indices.

### 2. Model Universe Theorem

`M(X)={point(X),line(X),plane(X)}`. Each model is constructed only from
finite sums and coordinate variances of X, with deterministic coordinate-index
tie breaking. Hence M(X) is finite, deterministic and observation-derived.

### 3. Boundary-Regularization Graph Theorem

`G_B(X)` contains every unordered point pair with

`w_ij=1/(1+||x_i-x_j||/diam(X))`.

For `n>1` it is complete, finite and strictly positive, so the normalized cut
`B_X(P)=cut_w(P)/sum_E w_e` is a canonical X-derived regularizer.

### 4. Observation-derived energy domain

`E_X(P)=sum_A min_{m in M(X)}[F_X(A,m)+k(m)] + B_X(P)`.

The coefficients of model complexity and boundary regularization are frozen at
`1`. The strict-separation quantity is not an input. Instead

`delta_X=min{|E_X(P)-E_X(Q)|:P not~Q, gap>0}`

over the finite `Gamma(X)`, with `delta_X=0` if no positive gap exists.

### 5. Observation-derived stability domain

For a Unit support `S`, `N_X(S)` consists of one-index insertion/deletion
moves. `S_X(S)` consists of every non-empty proper subset. Both are finite and
closed under observation-index relabeling.

### 6. Observation-derived relation domain and predicate

For a materialized world with `k` Units,

`C_R(X)={(i,j):0<=i,j<k, i!=j}`.

Freeze `Q_X(u_i,u_j)` to mean that the normalized minimum cross-support
distance is finite and its confidence `1/(1+d_X)` is positive. For valid
finite X, every distinct non-empty pair satisfies Q_X. The relation layer
records the distance and confidence as evidence. The separate Stage 3B
Hausdorff-contact predicate remains available as a stronger optional relation
theorem and is not silently identified with Q_X.

### 7. Observation-derived representation

`Phi_X(W)` is the fixed 23-coordinate map implemented in
`theory_representation.py`. Its groups are finite histograms, counts,
confidence statistics, occupancy statistics, and topology counts. Every group
is invariant to Unit relabeling. This proves well-definedness on the finite
quotient; it does **not** prove injectivity or semantic completeness.

## D. Non-negotiable boundaries

1. Legacy `structure/energy.py` remains regression-only.
2. No semantic label enters any observation-derived boundary.
3. No neural network is used to define `A_max`, `M`, `G_B`, `N_X`, `S_X`, `C_R`,
`Q_X`, or `Phi_X`.
4. Deterministic tie-breaking is not uniqueness.
5. Object, Instance, and Hierarchy remain separate theory problems.
6. The observation-derived representation is a well-defined coordinate map,
not an injective encoding theorem.
7. Stage 2D separation margin is a derived property of the finite family, not a
circular additive energy term.

## E. Release criterion

The theory-compliant core is regression-clean only when the full
`python -m unittest discover -s tests -v` suite passes. The new observation path
is complete at the interface level when the observation-derived regression
suite also passes.
