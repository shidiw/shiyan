# Struct3D mathematics → engineering-code contract

This document is the release gate for the `refactor/theory-compliant-core`
branch. The mathematical theory is authoritative. Historical engineering
descriptions are evidence, not automatic definitions.

## A. Observation-derived closure map

| Boundary | Observation-derived definition | Engineering location | Status |
|---|---|---|---|
| `A_max(X)` | complete finite partition lattice `Pi(Omega_X)` | `structure/theory_candidates.py` | **Implemented mathematical universe** |
| `Gamma(X)` | finite scalable family `Gamma(X) subset A_max(X)` | `structure/theory_candidate_search.py` | **Frozen computational family** |
| `A_search(X)` | compatibility alias of `Gamma(X)` only | `structure/theory_candidate_search.py` | **Scalability approximation; not canonical provenance** |
| `M(X)` | point, line, plane models fitted deterministically to X | `structure/theory_observation.py` | **Frozen** |
| `G_B(X)` | complete weighted observation graph with `w_ij=1/(1+d_ij/diam(X))` | `structure/theory_observation.py` | **Frozen** |
| `N_X` | one-index insertion/deletion neighborhood | `structure/theory_observation.py` | **Frozen observation-derived boundary** |
| `S_X` | one-point deletions plus singleton supports | `structure/theory_observation.py` | **Frozen scalable local family** |
| `Can_U^X` | sorted observed support multiset + frozen `theta`; complete invariant of the finite Unit quotient | `structure/theory_unit_invariant.py` | **Frozen complete invariant** |
| `C_R(X)` | all ordered pairs of distinct selected Units | `structure/theory_observation.py`, `theory_observation_pipeline.py` | **Frozen from selected Unit lineage** |
| `Q_X` | minimum cross-support distance <= median pairwise distance on the local union | `structure/theory_semantic_observation.py` | **Unique frozen relation law** |
| legacy H^2 / weak proximity laws | historical compatibility constructors | `structure/theory_relation_formation.py` | **Regression/experimental only; not theory** |
| `Phi_X` | fixed 23-D structural statistics of `(X,W)` | `structure/theory_representation.py` | **Implemented coordinate map** |
| Stage 2D `E_X` | canonical energy consuming `M(X)` and `G_B(X)` with frozen weights `(1,1)` | `structure/theory_energy_model.py` | **Frozen observation-derived constructor** |
| `delta_X` | minimum positive quotient-distinct energy gap in Gamma | `structure/theory_energy_model.py` | **Derived, never externally supplied** |
| Stage 2E | `Stable -> MinimalStable -> Unit` using `N_X`, `S_X`, X-derived competitors | `structure/theory_unit_formation.py`, `theory_stage2e_existence.py` | **Executed and existence-closed by canonical observation-derived theorem** |
| Unit → Relation | selected Units + unique `Q_X` | `structure/theory_semantic_relation.py` | **Canonical observation path** |
| Relation → World | copies canonical Q_X relations into `W=(U,R,Phi)` | `structure/theory_observation_pipeline.py`, `theory_world.py` | **Implemented** |
| World → Representation | `Phi_X(W)` from the same observation context | `structure/theory_representation.py` | **Implemented** |

## B. Preserved frozen objects

- Structural Unit: `u=(G,theta)`.
- Explicit Relation: `r=(source,target,type,evidence)`.
- Structural Graph: `G=(V,E)` with edges copied from the canonical relation set.
- Structural World: `W=(U,R,Phi)`.
- Canonical form: exact finite `C(W)`.
- Structural invariant: `I(W)=C(W)`.
- Unit quotient invariant: `Can_U^X(u)`.
- Representation distance: `D_R=||Phi_X(W1)-Phi_X(W2)||_2`.

## C. Mathematical contracts of the upstream closure

### 1. Candidate domain

For `Omega_X={0,...,n-1}`,

`A_max(X)=Pi(Omega_X)`.

The runtime does not enumerate this exponential mathematical universe for
large observations. It instead evaluates the frozen finite `Gamma(X)` family.

`Gamma(X) subset A_max(X)` and every Gamma candidate is deterministic from X,
finite, non-empty, valid, and quotient compatible. `A_search(X)` is only a
backward-compatible scalability approximation and is explicitly excluded from
the canonical pipeline.

### 2. Model and boundary objects

`M(X)={point(X),line(X),plane(X)}`.

`G_B(X)` is complete with

`w_ij=1/(1+||x_i-x_j||/diam(X))`.

Both are generated directly by `ObservationDerivedContext`.

### 3. Stability and Unit formation

For a candidate Unit support `S`,

`N_X(S)` consists of one-index insertion/deletion alternatives.
`S_X(S)` consists of one-index deletions and singleton supports.

The canonical pipeline explicitly evaluates

`Stable_X(S) -> MinimalStable_X(S) -> materialize_observation_unit(S)`.

### 4. Observation-Derived Stage 2E Existence Theorem

Because `Gamma(X)=A_max(X)=Pi(Omega_X)`, the X-derived Unit family contains
every non-empty support of the finite observation. Therefore every `N_X`
alternative is another member of the same finite Unit family. The Stage 2D
unit energy is finite on this family, so a global unit-energy minimizer exists
and is locally stable. The stable Unit subset is consequently finite and
non-empty. Selecting a stable Unit with minimum support cardinality eliminates
every stable proper subcandidate in the frozen `S_X` family, whose members have
strictly smaller support cardinality. Hence a legal `Stable_X ∧ MinimalStable_X`
Unit exists for every valid finite observation under the canonical zero-margin
Stage 2E contract.

The proof is implemented and regression-tested in
`structure/theory_stage2e_existence.py` and
`tests/test_observation_stage2e_existence.py`.

### 5. Complete Unit quotient invariant

For `u=(G,theta)`, freeze

`Can_U^X(u) = ( sort({x_i : i in G}), Freeze(theta) )`.

The index names are removed, while the complete finite observed support
multiset and frozen Unit attributes are retained. Therefore

`Can_U^X(u)=Can_U^X(v) <=> u ~_X v`.

The theorem and regression implementation are in
`structure/STRUCT3D_ENERGY_INDUCED_UNIT_EQUIVALENCE_THEOREM.md`,
`structure/theory_unit_invariant.py`, and
`tests/test_theory_unit_invariant.py`.

Stage 2D now accepts the observation-aware invariant through
`unit_quotient_key(unit, observation)` and uses it for quotient-distinct
energy-gap calculations. The old raw-index key remains only as a compatibility
API when no observation is supplied.

### 6. Strict Unit margin is derived, not assumed

Define the global pairwise Unit separation

`Delta_U(X) = min { |E_U,X(u)-E_U,X(v)| : u,v in U_X, u != v }`.

A tie forces `Delta_U(X)=0`; hence `Delta_U(X)>0` is exactly strict pairwise
separation of the complete X-derived Unit family. This quantity is diagnostic
and observation-derived, but it does not by itself prove MinimalStable.

The actual strict Stage 2E margin is checked only for a witness satisfying
both `Stable_X` and `MinimalStable_X` and the directional condition

`E_U,X(v)-E_U,X(u) >= delta > 0` for every distinct `v in U_X`.

### 7. Unique relation law

For distinct non-empty Units A and B, freeze

`Q_X(A,B) <=> d_cross(A,B) <= median{ ||x_p-x_q|| : p,q in A union B, p<q }`.

This is the only relation predicate with frozen theory status.
The previous complete-proximity predicate and H^2 boundary-contact law remain
available solely for regression/experimental compatibility and cannot be used
by the canonical World construction.

### 8. Representation lineage

The selected Unit partition determines `C_R(X)`. The same selected Units and
same `ObservationDerivedContext` determine `Q_X`, the relation set, World and
`Phi_X`. Therefore the canonical path has one provenance lineage rather than
independent external relation or representation inputs.

## D. Non-negotiable boundaries

1. Legacy `structure/energy.py` remains regression-only.
2. No semantic label enters any observation-derived boundary.
3. No neural network defines `A_max`, `Gamma`, `M`, `G_B`, `N_X`, `S_X`, `C_R`,
   `Q_X`, World or `Phi_X`.
4. `A_search` must never be described as `A_max` or used as the theorem-level
   candidate family.
5. The legacy H^2 and weak proximity relation laws must never be described as
   co-equal alternatives to the frozen `Q_X`.
6. Deterministic tie-breaking is not uniqueness.
7. Object, Instance and Hierarchy remain separate theory problems.
8. `Can_U^X` is complete only for the frozen finite Unit quotient; it does not
   prove that the 23-D `Phi_X` is injective on World space.

## E. Release criterion

The theory-compliant core is regression-clean only when the full
`python -m unittest discover -s tests -v` suite passes. The observation-facing
release path is complete only when the upstream closure tests also verify that
`A_search` is not called, Stage 2E existence is observation-derived, `Can_U^X`
is invariant and complete for Unit relabeling, the unique `Q_X` law generates
relations, and `C_R -> World -> Phi_X` uses the selected X-derived Unit lineage.
