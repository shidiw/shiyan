# Struct3D mathematics → code contract

This document is the release gate for the theory-compliant core. A row may be
called **implemented** only when the Python object and its regression contract
match the mathematical statement; a legacy implementation is never promoted
by naming alone.

| Mathematical object / statement | Code | Status |
|---|---|---|
| Structural Unit `u=(G,theta)` | `structure/theory_unit.py::StructuralUnit` | Implemented as the single Unit type; support and attributes are explicit |
| Compatibility name `TheoryUnit` | `structure/theory_core.py::TheoryUnit` | Alias only; no second Unit model exists |
| Finite partition validity | `structure/theory_core.py::Partition` | Implemented: nonempty, disjoint, complete |
| Scalar energy functional supplied on a partition | `structure/theory_energy.py` | Interface implemented; no unsupported decomposition claimed |
| Generic finite argmin | `structure/theory_partition.py` | Implemented over explicit admissible candidates |
| Unit materialization from a valid partition | `structure/theory_materialization.py` | Identity on partition cells; no hidden discovery |
| Explicit relation `r=(source,target,type,evidence)` | `structure/theory_relation.py` | Implemented |
| Structural graph `G=(V,E)` | `structure/theory_world.py` + graph tests | Implemented; edges are exactly supplied relations |
| Structural World `W=(U,R,Phi)` | `structure/theory_world.py` | Implemented domain/container contract |
| Canonical form `C(W)` | `structure/theory_canonical.py` | Exact finite exhaustive construction |
| Structural invariant `I(W)=C(W)` at the frozen finite level | `structure/theory_invariant.py` | Explicit stage; no second unsupported statistic introduced |
| Structural representation `phi(W) in R^23` | `structure/theory_representation.py` | Dimension/schema frozen; canonical path consumes `I(W)` |
| Representation distance `D_R=||phi(W1)-phi(W2)||_2` | `structure/theory_distance.py` | Direct implementation |
| Matching `M* in argmin_{M in A} C(M)` | `structure/theory_matching.py` | Explicit candidate/cost argmin; cost decomposition remains external |
| Object | `structure/theory_object.py` | Derived engineering construction, not promoted to theorem |
| Instance | — | Theory gap; intentionally not implemented |
| Hierarchy | — | Theory gap; intentionally not implemented |
| Neural latent distance equals structural distance | `structure/theory_neural_objective.py` | Objective/validation contract only; equality is not claimed |

## Non-negotiable boundaries

1. Legacy `structure/energy.py` and legacy partition discovery are regression
   baselines. They are not imports into the theory core.
2. No curvature threshold, distance threshold, minimum-size filter, or
   primitive classifier may silently become a mathematical definition.
3. `D_R=0` proves equality of the supplied 23-D representations, not structural
   equivalence, unless injectivity of `phi` is separately established.
4. A deterministic tie-break in an argmin implementation does not establish
   mathematical uniqueness.
5. `Object`, `Instance`, and `Hierarchy` must not be promoted into the frozen
   theory without an explicit mathematical definition.
6. The neural objective must not be reported as a proof of latent metric
   preservation. That property requires an independent experiment/proof.

## Release criterion

The theory-compliant core is considered regression-clean when the full
`python -m unittest discover -s tests -v` suite passes and no test depends on
legacy heuristics to construct a theory object.
