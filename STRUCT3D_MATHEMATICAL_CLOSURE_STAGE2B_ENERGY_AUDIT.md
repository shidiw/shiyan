# Struct3D Mathematical Closure — Stage 2B Energy Audit

## 0. Audit status

This is the accelerated Stage 2B audit of the `refactor/theory-compliant-core` branch.

The purpose is to determine, without inventing mathematics, whether the historical energy model is closed against the current mathematical specification and engineering implementation.

The governing rule is:

`mathematical definition -> derivation/proof -> engineering implementation -> regression contract`

A legacy implementation is evidence of project history, not automatically a theorem.

## 1. Authoritative upstream statement

The preserved Struct3D mathematical document defines the early formation problem through an observation, admissible structural candidates/partitions, energy minimization, and subsequent structural formation. It also preserves the historical additive energy skeleton

`E = E_fit + lambda_c C + lambda_b B`.

The same material distinguishes the later frozen chain

`W -> C(W) -> I(W) -> phi(W) -> D_R -> M -> neural extension`

from the still-unclosed upstream construction of Structural Units.

Therefore the audit does NOT replace the historical energy skeleton with a new `geometry + boundary + spatial` formula.

## 2. Current theory-facing code

`structure/theory_energy.py` intentionally accepts an externally supplied scalar functional. It validates finiteness but does not introduce default weights, primitive dimensions, thresholds, or regularizers.

`structure/theory_core.py` similarly treats the candidate family and energy functional as explicit external inputs. `select_minimizer` implements an argmin over a supplied finite candidate set.

This is mathematically conservative and is consistent with the current theory boundary.

## 3. Legacy engineering energy

`structure/energy.py` implements the historical engineering form

`E(U) = E_fit + lambda_complexity * E_complexity + gamma_boundary * E_boundary`.

Its concrete components are:

- primitive-specific plane/sphere/cylinder squared fitting residuals;
- a primitive parameter-dimension table (`plane=4`, `sphere=4`, `cylinder=5`, unknown=10);
- a centroid/radius-dispersion variance used as a boundary surrogate;
- default weights `lambda_complexity=0.01` and `gamma_boundary=0.01`.

These quantities are retained as legacy regression behavior. They are NOT promoted to the frozen mathematical definitions of `E_fit`, `C`, or `B`.

## 4. Energy closure verdict

### 4.1 Additive skeleton

`E = E_fit + lambda_c C + lambda_b B`

**STATUS: HISTORICALLY PRESERVED / FORMAL SKELETON ONLY.**

The existence of the additive structure is supported, but the exact domains, normalization, units, and mathematical definitions of all three terms are not sufficiently frozen to claim a complete energy theorem.

### 4.2 Exact fitting functional

**STATUS: THEORY GAP.**

The legacy primitive-specific residuals are concrete engineering formulas, but the current frozen theory does not establish that primitive fitting is the unique or required definition of `E_fit` for every Structural Unit.

### 4.3 Complexity functional

**STATUS: THEORY GAP.**

The legacy parameter-count mapping is an engineering heuristic/model choice. No frozen theorem currently proves that complexity must equal primitive parameter dimension, nor that the value is invariant under the structural equivalences used later.

### 4.4 Boundary functional

**STATUS: THEORY GAP.**

The legacy centroid/radius-variance quantity is explicitly documented as an early surrogate and is not a mathematically frozen boundary measure. It therefore cannot be promoted to `B` without a new definition and justification.

### 4.5 Normalization / scale

**STATUS: THEORY GAP.**

The current theory does not establish the normalization needed for energy comparison across different sampling densities, observation scales, or point counts. Consequently an absolute universal energy threshold is not justified.

## 5. Stability cannot yet be derived from energy alone

The following statements are NOT currently frozen laws:

- `E(A) < tau -> A is a Structural Unit`;
- `exp(-E(A)) log(|A|+1)` as a canonical stability score;
- a universal threshold such as `0.1`;
- `Delta E_merge < 0` as the official Unit-emergence theorem.

A pairwise merge delta can be studied later, but it must first be related formally to the admissible perturbation/splitting family and to the global partition objective.

## 6. Required mathematical objects for the next closure stage

Before adding theory-facing energy/stability code, the following must be frozen:

1. **Admissible candidate family** `A(X)` — what subsets/partitions are admissible and why.
2. **Exact energy domain** — whether `E` acts on a region, a partition, or both.
3. **Exact `E_fit`** — definition, parameter space, residual, normalization.
4. **Exact complexity `C`** — definition and structural invariance requirements.
5. **Exact boundary `B`** — definition and relation to the geometry/topology of a candidate.
6. **Well-posedness assumptions** — finiteness, boundedness below, and existence of a minimizer for the declared candidate family.
7. **Stability predicate** — the allowed perturbations/splits and the exact inequality.
8. **Minimality predicate** — what makes a stable region minimal rather than merely stable.
9. **Unit emergence theorem** — sufficient conditions under which a selected stable/minimal candidate is a Structural Unit.

## 7. Current closed chain

The theory-safe chain that is currently implemented is:

`finite observation universe X`

`-> explicit finite candidate family A(X)`

`-> P* in argmin_{P in A(X)} E(P)`

`-> materialization of valid partition cells`

`-> StructuralUnit`

`-> StructuralWorld W=(U,R,Phi)`

`-> canonical/invariant representation`

`-> 23-D representation`

`-> Euclidean representation distance`

`-> explicit matching`

The upstream implication

`stable/minimal candidate -> uniquely or canonically formed Structural Unit`

remains open.

## 8. Downstream audit result

The downstream v3.6-v4.0 implementation is deliberately conservative:

- canonicalization is finite and exact for the declared finite validation regime;
- the frozen invariant is `I(W)=C(W)`;
- representation dimension is frozen at 23, while numerical extraction is kept explicit;
- `D_R(W1,W2)=||phi(W1)-phi(W2)||_2` is implemented as representation-space distance;
- zero representation distance is not promoted to structural identity without injectivity;
- neural reconstruction is not promoted to latent metric preservation.

Thus the major remaining mathematical risk is upstream structural formation, not the already audited downstream representation-distance contract.

## 9. Release decision

**NOT YET MATHEMATICALLY CLOSED.**

The engineering branch is contract-clean according to the user's latest local regression result (`90 tests ... OK`), but this proves implementation-contract consistency, not the missing energy/stability theorems.

The correct next step is Stage 2C: formalize `Stable(A)` and `Minimal(A)` from the preserved theory, then determine whether any merge/split inequality is a theorem, a sufficient condition, or only a heuristic.

No theory-facing implementation of a new energy decomposition or stability threshold should be added before Stage 2C.
