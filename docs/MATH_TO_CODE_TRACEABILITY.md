# Struct3D Mathematics → Code → Regression Traceability

This document is the formal gate between the established Struct3D mathematics and the refactor branch. It does not create new mathematics.

## Status vocabulary

- **CERTIFIED** — explicit formal statement, direct implementation, and regression coverage.
- **PARTIAL** — interface/invariant exists, but complete mathematical derivation or exact semantics are not yet encoded.
- **LEGACY** — historical engineering behavior; tested only for regression.
- **UNVERIFIED** — requires the authoritative mathematics source before equivalence can be claimed.

## Traceability matrix

| Mathematical role | Code | Regression | Status |
|---|---|---|---|
| Unit is a non-empty indexed subset with parameters | `structure/theory_core.py:TheoryUnit` | `tests/test_theory_core.py` | CERTIFIED |
| Partition is pairwise-disjoint and complete | `structure/theory_core.py:Partition` | `tests/test_theory_core.py` | CERTIFIED |
| Scalar Energy functional on partitions | `structure/theory_energy.py:StructuralEnergy` | `tests/test_theory_energy.py` | CERTIFIED |
| Stable selection as argmin over explicit candidates | `structure/theory_partition.py:select_stable_partition` | `tests/test_theory_partition.py` | CERTIFIED |
| Legacy `E_fit + lambda*C + gamma*B` | `structure/energy.py` | `tests/test_legacy_energy_unit.py` | LEGACY |
| Legacy threshold/connected-component/min-size partition | `structure/graph_cluster.py` | `tests/test_legacy_energy_unit.py` | LEGACY |
| Explicit structural Relation | `structure/theory_relation.py` | `tests/test_theory_structure.py` | PARTIAL |
| Assembly from explicitly designated relations | `structure/theory_object.py` | `tests/test_theory_structure.py` | PARTIAL |
| Structural World container | `structure/theory_world.py` | `tests/test_theory_structure.py`, pipeline test | PARTIAL |
| Relabeling-invariant canonical form | `structure/theory_canonical.py` | `tests/test_theory_structure.py` | PARTIAL |
| 23D structural representation | `structure/theory_representation.py` | `tests/test_theory_representation_distance.py` | PARTIAL |
| `D_R(W1,W2)=||phi(W1)-phi(W2)||_2` | `structure/theory_distance.py` | `tests/test_theory_representation_distance.py` | CERTIFIED at formula level |
| Minimum-cost structural matching | `structure/theory_matching.py` | `tests/test_theory_representation_distance.py` | PARTIAL |
| Reconstruction objective | `structure/theory_neural.py` | `tests/test_theory_representation_distance.py` | CERTIFIED at objective level |
| Distance-preserving neural objective | `structure/theory_neural.py` | `tests/test_theory_representation_distance.py` | PARTIAL |
| Mutation consistency objective | `structure/theory_neural.py` | `tests/test_theory_representation_distance.py` | PARTIAL |

## Critical conclusion

The current 36/36 regression result proves implementation consistency of the present Core and its explicit invariants. It does **not** prove that every line is a faithful implementation of the historical Struct3D mathematical derivation.

Before Phase 2 is called theory-complete, the authoritative mathematics version must be recovered and every numbered Definition, Proposition, Theorem, and formula must be mapped to exact code and one or more regression tests.

A regression test is not evidence that a heuristic is mathematically valid. Historical thresholds, weights, connected components, primitive parameter-count penalties, and similar choices remain LEGACY unless explicitly derived by the established theory.

## Current safe implementation chain

`P -> admissible candidate partitions -> E -> Pi* -> U -> explicit R -> W -> C(W) -> phi(W) -> D_R -> M -> neural objectives`

Only the portions marked CERTIFIED above may currently be described as direct mathematical-to-code equivalence.
