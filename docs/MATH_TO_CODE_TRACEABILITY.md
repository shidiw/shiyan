# Struct3D Mathematics → Code → Regression Traceability

Source of truth: `structure/Struct3D_数学理论.txt` on this refactor branch. This document does not create new mathematics.

## Status vocabulary

- **CERTIFIED** — the supplied mathematical statement is explicit, the implementation directly represents it, and regression coverage tests the stated property.
- **PARTIAL** — some structure is implemented, but the supplied document does not fully freeze the numerical/algorithmic semantics.
- **LEGACY** — historical engineering behavior; retained only for compatibility/regression.
- **PROVISIONAL** — mathematically valid generic scaffold, but the supplied specification does not define it as a Struct3D construction.
- **THEORY GAP** — the engineering pipeline needs a mathematical construction that is absent from the supplied specification.

## Frozen theory → code → regression

| Mathematical statement | Code | Regression | Status |
|---|---|---|---|
| `u_i=(G_i,theta_i)` | `structure/theory_core.py:TheoryUnit` | `tests/test_theory_core.py` | CERTIFIED container mapping |
| `r_ij` is a relation between two Units | `structure/theory_relation.py:StructuralRelation` | relation/world tests | CERTIFIED container mapping |
| Relation evidence may depend on geometry/boundary/spatial information | `StructuralRelation.evidence` | relation tests | CERTIFIED representation of explicit evidence; inference rule remains external |
| `G=(V,E)` | `structure/theory_graph.py:StructuralGraph` | graph property tests | CERTIFIED |
| `W=(U,R,Phi)` | `structure/theory_world.py:StructuralWorld` | world/pipeline tests | CERTIFIED container mapping |
| `W ~_label pi(W)` | `structure/theory_canonical.py` | `tests/test_theory_math_properties.py` | CERTIFIED at finite-container level |
| `C(W)=C(pi(W))` | `canonical_form()` | all tested unit permutations | CERTIFIED |
| `I(W)=I(pi(W))` | `structure/theory_invariant.py:structural_invariant` | `tests/test_theory_math_properties.py` | CERTIFIED for the canonical-form invariant |
| `phi(W) in R^23` | `structure/theory_representation.py:StructuralRepresentation` | representation tests | CERTIFIED dimension contract |
| seven v4.0 coordinate groups `(3,3,3,3,3,3,5)` | `structure/theory_representation_schema.py` | `tests/test_theory_representation_schema.py` | CERTIFIED schema contract |
| `D_R=||phi(W1)-phi(W2)||_2` | `structure/theory_distance.py` | distance tests | CERTIFIED formula |
| non-negativity, symmetry, triangle inequality | `theory_distance.py` | `tests/test_theory_math_properties.py` | CERTIFIED from Euclidean norm |
| `D_R=0 iff phi(W1)=phi(W2)` | Euclidean distance implementation | `tests/test_theory_math_properties.py` | CERTIFIED in representation space |
| representation-level mutation changing `phi` gives nonzero `D_R` | distance definition | distance/mutation tests | CERTIFIED conditional statement |
| matching is an optimization over admissible correspondences | `structure/theory_matching.py` | matching tests | CERTIFIED generic optimization |
| complete matching cost `C_ij=d_u+lambda_r d_r+lambda_g d_g` | external cost callable | matching tests | PARTIAL: framework stated, final cost not frozen |

## Representation: an important boundary

The supplied document freezes the 23-dimensional grouping but does **not** freeze a unique numerical estimator for every coordinate. Therefore the core representation object validates the exact coordinate contract but does not invent feature formulas. A concrete extractor must establish relabeling invariance before it is promoted as the canonical Struct3D extractor.

## Neural theory boundary

The supplied document distinguishes the v1.0 reconstruction objective from the later distance-preserving direction. `structure/theory_neural.py` therefore exposes these objectives separately. The combined

`L = L_recon + lambda_d L_distance + lambda_m L_mutation`

is treated as a later proposed objective, not retroactively attributed to v1.0. Network architecture, training hyperparameters, and a claim that latent distance exactly equals structural distance are not frozen mathematics.

## Deliberately provisional: Energy → Partition → Unit emergence

The supplied Struct3D mathematical document defines Structural Units and the later structural space, but it does **not** freeze a final raw-point energy functional, an admissible partition class generated from raw points, or a theorem deriving Units through

`Pi* = argmin_{Pi in A(P)} E(Pi)`.

Therefore:

- `structure/theory_energy.py` is an explicit scalar-functional interface, not a frozen Struct3D energy formula.
- `structure/theory_partition.py` is a generic finite argmin scaffold, not a claim that the supplied theory already defines Unit discovery this way.
- `structure/energy.py`, `graph_cluster.py`, and threshold/min-size rules are **LEGACY** engineering implementations and are not evidence for the theory.

This distinction is intentional. We must not invent an Energy merely to make the engineering pipeline look mathematically complete.

## Phase-1 gate

A frozen-theory component is promoted to CERTIFIED only when:

`mathematical statement == implementation == regression property`

If the mathematics is silent, the code remains explicitly provisional. If legacy code contradicts the mathematical specification, legacy code is not used as evidence for the theory.

### Current Phase-1 result

**Certified:** Structural Unit container, Relation container/evidence, Structural Graph, Structural World container, relabeling equivalence, exact finite canonicalization, canonical invariant, 23D representation schema, Euclidean Structural Distance and its metric-space properties, and generic matching optimization.

**Partial:** final numerical feature extractor, final matching cost, neural distance-preserving objective/architecture.

**Theory gap:** raw observation → candidate Structural Units / admissible partition → final Unit emergence. No legacy heuristic is promoted to fill this gap.

Only after this gate is satisfied should Phase 2 begin. Phase 2 may connect the certified structural objects to the legacy/raw-point pipeline, but it must not silently promote a heuristic into the frozen mathematics.
