# Struct3D Mathematical Closure — Stage 2 Audit (updated 2026-08-23)

## 1. Current closure boundary

The theory-compliant core now distinguishes two things that must not be conflated:

1. **Mathematical closure of the finite observation-derived execution boundary**: every formerly caller-supplied object required by the declared finite pipeline is constructed deterministically from the observation `X`.
2. **Unproved semantic claims**: global injectivity of the frozen 23-D representation and semantic completeness of `D_R` are deliberately *not* claimed.

The resulting closed engineering path is:

`X -> A_max(X)=Gamma(X) -> M(X), G_B(X), N_X, S_X, C_R(X) -> E_X -> argmin -> Unit -> R -> W -> Phi_X(W)`.

The low-level explicit-input APIs remain for generic mathematical/regression compatibility. They are not the closed raw-observation theorem path.

## 2. Status matrix

| Object / claim | Previous boundary | Current status | Evidence |
|---|---|---|---|
| `A(X)` non-empty | caller supplied | **CLOSED for finite non-empty observations** | `ObservationCandidateFamily.from_universe` constructs `Pi(Omega_X)` |
| `A(X)` finite | caller supplied | **CLOSED** | complete finite set-partition enumeration |
| candidate family quotient-compatible | contract | **CLOSED** | relabeling action preserves `Gamma(X)=Pi(Omega_X)` |
| `P*=argmin_A E` | finite theorem | **CLOSED** | finite candidate selection and regression tests |
| `P* -> U` | identity | **CLOSED** | partition materialization is exact |
| neighborhood `N_X(u)` | caller supplied | **CLOSED as a frozen observation-derived perturbation domain** | one-index insertion/deletion construction |
| proper subcandidate family `S_X(u)` | caller supplied | **CLOSED as a frozen observation-derived family** | all non-empty proper support subsets |
| geometric model family `M(X)` | caller supplied | **CLOSED** | deterministic point/line/plane model family |
| boundary graph `G_B(X)` | caller supplied | **CLOSED** | complete observation-derived weighted graph |
| `delta_E` | verified finite-family property | **DERIVED / CONDITIONALLY POSITIVE** | `Stage2DEnergy.derived_separation_margin`; positive only when no quotient-distinct energy ties occur |
| `U -> R` candidate pairs `C_R` | caller supplied | **CLOSED** | all ordered pairs of distinct materialized units |
| geometry evidence | caller supplied | **CLOSED** | all geometric terms are derived from `X` and `M(X)` |
| `R -> W` | explicit construction | **CLOSED** | `StructuralWorld` materialization |
| quotient World | existing boundary | **CLOSED** | canonical/relabeling tests |
| `W -> Phi` coordinate schema | frozen | **CLOSED** | frozen 23-D schema |
| concrete `Phi_X` formulas | caller extractor | **CLOSED** | `represent_observation` / `phi_x` implement all 23 coordinates |
| `Phi` global injectivity | not established | **NOT CLAIMED** | finite-set checker exists only as evidence tool |
| `D_R` semantic completeness | not established | **NOT CLAIMED** | Euclidean distance is defined, but completeness requires an independent theorem |

## 3. Important qualification about the upstream theory

The current implementation closes the **observation-derived finite boundary**. This does not retroactively prove that the historical prose contained a unique intended definition for every object.

The frozen implementation choices are now explicit:

- `Gamma(X)=Pi(Omega_X)`;
- `M(X)` contains point, line, and plane models;
- `G_B(X)` is complete with normalized inverse-distance weights;
- `N_X(u)` uses one-index insertion/deletion moves;
- `S_X(u)` contains all non-empty proper support subsets;
- `C_R(X)` contains all ordered pairs of distinct materialized units.

These are frozen definitions of the current theory-compliant finite core. They must not be presented as historical facts unless the authoritative mathematical manuscript independently supports them.

## 4. Energy and separation

The observation-derived Stage 2D energy is frozen as

`E_X(P) = sum_A [min_{m in M(X)} F_X(A,m) + k(m)] + B_X(P)`,

with normalized geometric residuals, fixed unit complexity coefficients, and the observation-derived boundary graph.

The separation statistic is

`delta_X = min { |E_X(P)-E_X(Q)| : P,Q in Gamma(X), P not~ Q, E_X(P) != E_X(Q) }`,

with `delta_X=0` when no positive gap exists.

Therefore `delta_X > 0` is **not** a universal theorem. It is a verifiable property of a particular finite observation/candidate family.

## 5. Representation boundary

The frozen representation is a concrete 23-coordinate map `Phi_X(W)`. Its coordinate construction is now fully implemented and regression-tested.

However, a fixed summary vector is not automatically injective over all possible Structural Worlds. The project therefore provides a finite-set `representation_injective_on(...)` checker, but deliberately does not promote a successful finite check to a global injectivity theorem.

Consequently:

`D_R(W_1,W_2)=||Phi_X(W_1)-Phi_X(W_2)||_2`

is a well-defined representation-space distance, but **semantic completeness** of this distance remains an open mathematical claim.

## 6. Regression contract added in this update

`structure/theory_closure.py` provides `ClosureCertificate` and `audit_observation_context(...)`.

`tests/test_theory_closure_certificate.py` verifies that the finite observation-derived boundary is non-empty, finite, quotient-compatible, geometrically derived, relation-complete, and concretely 23-dimensional, while explicitly asserting that representation injectivity and semantic completeness remain unclaimed.

## 7. Current release verdict

**The caller-supplied boundaries listed in the current closure table are now removed from the closed raw-observation execution path.**

The remaining non-closed mathematical claims are intentionally limited to:

1. a universal strict separation theorem `delta_X > 0`;
2. global injectivity of `Phi_X`;
3. semantic completeness of `D_R`.

These are not patched by arbitrary engineering assumptions. They require independent mathematical results or a deliberately frozen restricted theorem domain.
