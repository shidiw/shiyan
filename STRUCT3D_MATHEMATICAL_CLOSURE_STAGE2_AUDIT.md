# Struct3D Mathematical Closure — Stage 2 Audit

## Purpose

This document is a source-grounded comparison of the preserved Struct3D mathematical theory, the historical engineering description, and the current theory-compliant implementation on `refactor/theory-compliant-core`.

The audit does **not** invent missing mathematics. A statement is marked **CLOSED** only when the mathematical statement, engineering realization, and regression contract are mutually consistent. A historical statement without a frozen definition/proof is marked **HISTORICAL / GAP**. Legacy engineering behavior is not promoted merely because it exists.

## 1. Authoritative upstream chain

The preserved theory describes the early structural formation chain as:

`Observation X -> admissible partitions A(X) -> energy minimization -> stable region -> Structural Unit`.

The historical energy form recovered by Stage 1 is:

`E = E_fit + lambda_c C + lambda_b B`.

The historical theory also states the idea that a structural unit should be internally coherent and that splitting a candidate should increase the overall structural cost. However, the exact admissibility predicate and exact split/merge inequality are not frozen in the current authoritative theory.

Therefore this audit preserves the chain without assigning new formulas to its missing links.

## 2. Theory -> code -> tests matrix

| Stage | Mathematical statement | Current engineering realization | Tests / evidence | Verdict |
|---|---|---|---|---|
| Observation | An observation universe X is the input domain | `Partition.universe` is an explicit finite indexed universe | partition validation tests | CLOSED at finite indexed boundary |
| Candidate family | `A(X)` is the admissible partition family | Candidate partitions are supplied explicitly to selection functions | empty-set and minimizer tests | BOUNDARY; construction of `A(X)` is not frozen |
| Partition | Units are non-empty, disjoint, and complete over X | `Partition.__post_init__` enforces non-empty universe, domain validity, pairwise disjointness, and complete coverage | `test_partition_is_disjoint_and_complete`, overlap/incomplete/empty tests | CLOSED |
| Energy | Historical form `E_fit + lambda_c C + lambda_b B` | `StructuralEnergy` accepts an externally supplied scalar functional; no additive decomposition is invented | energy finite/NaN tests | BOUNDARY; exact E is a THEORY GAP |
| Legacy energy | Historical implementation exists | `structure/energy.py` remains legacy/regression code | legacy energy regression suite | LEGACY ONLY |
| Energy minimization | `P* in argmin_{P in A(X)} E(P)` for an explicit admissible finite set | `select_minimum_energy_partition` evaluates supplied energy and selects a minimum | minimizer tests | CLOSED for explicit finite candidate sets |
| Stable region | Candidate is structurally stable; historical text links stability to splitting cost | No frozen `Stable(A)` theorem or exact perturbation/split neighborhood is implemented | no valid theorem test exists yet | THEORY GAP |
| Pairwise merge delta | `E(A_i union A_j)-E(A_i)-E(A_j)` | No frozen merge-energy API/theorem | no theorem test | NOT FROZEN; do not add as law yet |
| Stability score | `exp(-E) log(|A|+1)` | No theory-facing implementation | none | NOT FROZEN; prior proposal must not be treated as theory |
| Fixed threshold | e.g. `S > 0.1` | Legacy thresholds exist in historical engineering | legacy regression tests | ENGINEERING CHOICE ONLY |
| Minimality | A formal minimal stable Unit | No frozen minimality definition/proof | none | THEORY GAP |
| Unit | `u_i=(G_i,theta_i)` | Single frozen `StructuralUnit` type | Unit boundary tests | CLOSED |
| Materialization | A valid partition cell can be materialized as a Unit | `theory_materialization.py` materializes already-valid cells without discovering them | materialization identity tests | CLOSED as a boundary operation |
| Relation | Explicit relation object; graph must use supplied relations | `theory_world.py` maps supplied Relations exactly | graph/relation tests | CLOSED |
| World | `W=(U,R,Phi)` | `StructuralWorld` implementation | world validation tests | CLOSED |
| Canonical form | Finite relabeling-invariant canonical representation | exact finite canonicalization | canonicalization tests | CLOSED for the declared finite regime |
| Invariant | Frozen finite invariant `I(W)=C(W)` | `theory_invariant.py` | determinism/relabeling tests | CLOSED at declared boundary |
| Representation | `phi(W) in R^23` with frozen grouping/dimension | explicit 23-D schema/interface | dimension/schema tests | CLOSED as a representation contract; extractor semantics remain bounded by the specification |
| Distance | `D_R(W1,W2)=||phi(W1)-phi(W2)||_2` | representation-space Euclidean distance | Euclidean/nonfinite/zero-distance tests | CLOSED |
| Matching | `M* in argmin_{M in A} C(M)` over explicit admissible set | explicit admissible-set matching | matching tests | CLOSED |
| Neural extension | latent metric preservation is a future property, not reconstruction alone | reconstruction/objective boundary only | neural objective contract tests | NOT A THEOREM; future research stage |

## 3. Energy audit

### 3.1 What is actually preserved

The historical theory supports an additive energy skeleton:

`E = E_fit + lambda_c C + lambda_b B`.

The current theory-facing implementation deliberately refuses to identify legacy implementation quantities with these abstract terms. In particular, the legacy primitive-specific fitting, primitive parameter-count complexity, and centroid/radius-variance boundary surrogate are not silently promoted to `E_fit`, `C`, or `B`.

### 3.2 What is not justified

The following are **not** frozen Struct3D mathematics at this stage:

- `E = w_g E_geometry + w_b E_boundary + w_s E_spatial`;
- `S(A) = exp(-E(A)) log(|A|+1)`;
- a universal stability threshold such as `0.1`;
- the pairwise merge delta as the official emergence theorem;
- a claim that low absolute energy alone defines a Unit.

These may be candidate research formulations later, but they are not to be represented as recovered historical theory.

## 4. Stability audit

The historical idea is stronger than "low energy": a Unit should be stable against an allowed structural perturbation, and the preserved text specifically mentions the cost increase caused by splitting.

The missing formal objects are therefore:

1. a neighborhood / admissible perturbation family around a candidate;
2. an exact stability predicate;
3. the relation between stability and partition optimality;
4. the minimality condition for a Unit;
5. existence conditions guaranteeing at least one admissible candidate.

Until these are recovered or explicitly derived and then frozen, the implementation must not invent a stability score or threshold.

## 5. Correct current mathematical closure

The part that can currently be written as a theorem-safe chain is:

`X (finite indexed universe)`

`-> A (explicit finite admissible candidate family)`

`-> P* in argmin_{P in A} E(P)`

`-> materialize valid partition cells as Structural Units`

`-> W=(U,R,Phi)`

The first arrow is an external boundary, the argmin is implemented, and Unit materialization is implemented. The missing implication is:

`stable/minimal candidate -> Structural Unit`

because `stable` and `minimal` are not yet mathematically frozen.

## 6. Required Stage 2 closure targets

The next mathematical work must proceed in this order:

### Target A — Admissibility

Recover or formally define `A(X)` without importing thresholds, connected components, primitive classifiers, or minimum point counts unless the mathematical specification explicitly requires them.

### Target B — Exact energy

Recover the exact definitions and domains of `E_fit`, `C`, and `B`, including their units, normalization, and dependence on the observation. Establish conditions under which the resulting functional is finite and comparable across admissible candidates.

### Target C — Stability

Recover the exact perturbation/splitting family and define `Stable(A)` from the authoritative theory. Only then decide whether a merge inequality is equivalent, sufficient, or merely a heuristic.

### Target D — Minimality

Define what "minimal Structural Unit" means and prove the relation between minimality and the chosen stability predicate.

### Target E — Existence / selection

State assumptions under which `A(X)` is non-empty and the energy minimization problem is well-posed. The current implementation already rejects an empty candidate family; that is an engineering contract, not an existence theorem.

### Target F — Engineering realization

Only after A-E are frozen should the theory-facing code gain concrete candidate generation, exact energy components, stability checks, or merge operations.

## 7. Release rule

No code change is justified merely because it makes the upstream chain look complete. A new theory-facing implementation is admissible only when:

`mathematical definition -> proof/derivation -> implementation -> regression contract`

is traceable for that object.

Until then, legacy code remains regression evidence and the current explicit-input boundary remains the correct implementation.

## 8. Current verdict

**Stage 2 audit established the comparison matrix. The downstream v3.x/v4.0 theory-to-code chain is substantially closed at its declared finite boundaries. The upstream formation problem is not yet mathematically closed. The highest-priority gaps are `A(X)`, exact `E`, stability, and minimality.**
