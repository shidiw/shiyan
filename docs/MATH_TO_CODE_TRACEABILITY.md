# Struct3D Mathematics → Code → Regression Traceability

Source of truth: `structure/Struct3D_数学理论.txt` on this refactor branch. This document does not create new mathematics.

## Status vocabulary

- **CERTIFIED** — explicit formal statement, direct implementation, and regression coverage.
- **PARTIAL** — interface/invariant exists, but complete mathematical derivation or exact semantics are not yet encoded.
- **LEGACY** — historical engineering behavior; tested only for regression.
- **PROVISIONAL** — mathematically valid scaffold, but the uploaded specification does not freeze the corresponding construction/formula.

## Traceability matrix

| Mathematical statement | Code | Regression | Status |
|---|---|---|---|
| `u_i=(G_i,theta_i)` | `structure/theory_core.py:TheoryUnit` | `tests/test_theory_core.py` | CERTIFIED container mapping |
| `r_ij` is a relation between two Units | `structure/theory_relation.py:StructuralRelation` | relation tests | CERTIFIED container mapping |
| `G=(V,E)` | `structure/theory_graph.py:StructuralGraph` | graph property tests | CERTIFIED |
| `W=(U,R,Phi)` | `structure/theory_world.py:StructuralWorld` | world/pipeline tests | CERTIFIED container mapping |
| relabeling equivalence `W ~ pi(W)` | `structure/theory_canonical.py` | canonicalization tests | CERTIFIED at finite-container level |
| `C(W)=C(pi(W))` | `canonical_form()` | relabeling test | CERTIFIED |
| `I(W)=I(pi(W))` | invariant extractor contract | extractor-specific tests required | PARTIAL |
| `phi(W) in R^23` | `structure/theory_representation.py` | dimension test | CERTIFIED dimension contract |
| seven v4.0 coordinate groups | `structure/theory_representation_schema.py` | schema tests required | CERTIFIED schema contract |
| `D_R=||phi(W1)-phi(W2)||_2` | `structure/theory_distance.py` | distance tests | CERTIFIED formula |
| non-negativity/symmetry/triangle inequality | `theory_distance.py` | property tests | CERTIFIED from L2 |
| representation-level mutation => nonzero `D_R` | distance definition | mutation tests | CERTIFIED conditional statement |
| matching is optimization over admissible correspondences | `structure/theory_matching.py` | matching test | CERTIFIED generic optimization |

## Deliberately provisional: Energy → Partition → Unit emergence

The uploaded specification defines Structural Units and the later structural
space, but it does **not** freeze a final Struct3D energy functional, an
admissible partition class generated from raw points, or a theorem deriving
Units through `Pi*=argmin E(Pi)`.

Therefore:

- `structure/theory_energy.py` is an explicit scalar-functional interface,
  not a frozen Struct3D energy formula.
- `structure/theory_partition.py` is a generic finite argmin scaffold, not a
  claim that the uploaded theory already defines Unit discovery this way.
- `structure/energy.py`, `graph_cluster.py`, and threshold/min-size rules are
  LEGACY engineering implementations and are not evidence for the theory.

This distinction is intentional. We must not invent an Energy merely to make
the engineering pipeline look mathematically complete.

## Matching cost

The mathematical document presents a framework of the form
`C_ij = d_u + lambda_r d_r + lambda_g d_g`, but explicitly says the complete
final cost was not frozen. The implementation therefore keeps the cost as an
external callable.

## Representation feature values

The document freezes the 23-dimensional grouping but does not give a unique
numerical estimator for every coordinate. The code therefore freezes the
coordinate contract without inventing feature formulas. A concrete extractor
must prove relabeling invariance before it is promoted to the theory layer.

## Neural objective

The reconstruction objective and later distance-preserving direction remain
separate. The combined distance/mutation objective is a later proposed
improvement and is not retroactively attributed to v1.0.

## Gate rule

A component may be promoted to CERTIFIED only when:

`mathematical statement == implementation == regression property`

If the mathematics is silent, the code remains explicitly provisional. If
legacy code contradicts the mathematical specification, legacy code is not
used as evidence for the theory.

## Phase-1 conclusion

The canonical / invariant / representation / distance portion can now be
traced directly to the uploaded mathematical specification. The missing
mathematical bridge is the raw-observation-to-Unit-emergence mechanism. That
is a **theory gap**, not a coding bug. Phase 2 must not claim to have solved
that gap until the Energy/Partition/Unit construction is formally derived or
the mathematics document is extended with the already-established derivation.
