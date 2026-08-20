# Struct3D mathematics → engineering-code contract

This document is the release gate for the `refactor/theory-compliant-core` branch.
The mathematical theory is authoritative. Historical engineering descriptions
are evidence of project history, not automatic definitions.

A row is **implemented** only when the Python object and its regression contract
match the mathematical statement. A legacy implementation is never promoted by
naming alone.

## A. Complete theory → code map

| Theory stage | Mathematical content | Engineering location | Status |
|---|---|---|---|
| v0.0 Geometry / observation | Observation is the input to structural construction | `data/` and legacy geometry modules | **Legacy implementation; not frozen theory** |
| v0.1 Geometric field | Geometry-derived quantities | `geometry/` | **Legacy implementation; no frozen theorem** |
| v0.2 Primitive Structural Unit | Historical primitive/geometry construction | legacy `structure/` modules | **Legacy implementation; primitive is optional metadata in the frozen Unit model** |
| v0.3 Structural Graph | Explicit `G=(V,E)` | `structure/theory_world.py` | **Implemented**; vertices are world Units and edges are exactly supplied Relations |
| v0.4 Structural Refinement | Refinement/optimization procedure | legacy optimization/refinement code | **Theory gap; intentionally not promoted** |
| v0.5 Structural Unit Discovery | A mathematically defined discovery operator | `structure/theory_materialization.py` | **Boundary only**; discovery is not silently invented |
| v0.6 Primitive Discovery | Primitive inference from geometry | legacy primitive modules | **Theory gap; intentionally not implemented in the frozen core** |
| v0.7 Primitive Energy | A frozen mathematical primitive energy functional | legacy `structure/energy.py` | **Theory gap**; legacy energy remains a regression baseline |
| v0.8 Hierarchy + Relation | Explicit Relations; higher hierarchy | `structure/theory_relation.py`, `structure/theory_world.py` | **Relation object implemented; hierarchy not promoted** |
| v0.9 Memory + Prototype | Structural memory/prototype theory | legacy memory/prototype modules | **Theory gap; intentionally not implemented** |
| v1.0 Structural World | `W=(U,R,Phi)` | `structure/theory_world.py` | **Implemented** |
| v1.x Unit | `u_i=(G_i,theta_i)` | `structure/theory_unit.py::StructuralUnit` | **Implemented** as the single frozen Unit type |
| v2.x Assembly / Object | Object emerges from explicitly defined assembly relations | `structure/theory_object.py` | **Derived engineering construction only**; not a frozen theorem |
| v2.x Instance | Instance identity and invariance | — | **Theory gap** |
| v2.x Hierarchy | Hierarchical structural object | — | **Theory gap** |
| v3.1–v3.5 equivalence/isomorphism/quotient | Structural equivalence machinery | `structure/theory_canonical.py` | **Finite canonical boundary implemented** |
| v3.6 Canonical Structural Form | `C: W -> C`, invariant under legal relabeling | `structure/theory_canonical.py` | **Implemented** |
| v3.7 Structural Invariant | `I(W)=I(pi(W))`; frozen finite choice `I(W)=C(W)` | `structure/theory_invariant.py` | **Implemented** |
| v3.8 Structural Distance | `D_R(W1,W2)=||phi(W1)-phi(W2)||_2` | `structure/theory_distance.py` | **Implemented** |
| v3.9 Structural Matching | `M* in argmin_{M in A} C(M)` | `structure/theory_matching.py` | **Implemented** over an explicit admissible set |
| v4.0 Structural Representation | `phi(W) in R^23` | `structure/theory_representation.py`, `structure/theory_representation_schema.py` | **Schema/interface implemented** |
| Neural Struct3D v1.0 | `z=f_theta(phi(W))`, reconstruction objective | `structure/theory_neural_objective.py` and neural code | **Objective/validation boundary only** |
| Distance-preserving neural extension | `D_Z approx D_R` | future neural implementation | **Not yet a theorem or completed algorithm** |
| Stage 2A–2D | Explicit candidates, energy domain, stability, frozen energy model | `structure/theory_admissible.py`, `structure/theory_stability.py`, `structure/theory_energy_model.py` | **Implemented as explicit contracts** |
| Stage 2E | `Materializable(u) <=> Stable(u) and MinimalStable(u)` | `structure/theory_unit_formation.py` | **Implemented boundary** |
| Stage 2F | finite non-empty `A(X)` + finite `E` => attained `argmin` | `structure/theory_existence.py` | **Conditional theorem implemented and tested** |
| Stage 2G | strict energy separation => singleton `argmin` | `structure/theory_uniqueness.py` | **Conditional theorem implemented and tested** |
| Stage 3 | `R_Q={r_ij:(i,j) in C_R, Q(u_i,u_j)=True}` | `structure/theory_relation_formation.py` | **Implemented explicit relation-formation boundary; geometry-to-Q theorem remains open** |

## B. Frozen mathematical objects

- Structural Unit: `u=(G,theta)`.
- Explicit Relation: `r=(source,target,type,evidence)`.
- Structural Graph: `G=(V,E)` with `V` indexed by world Units and `E` copied exactly from Relations.
- Structural World: `W=(U,R,Phi)`.
- Canonical form: exact finite `C(W)`.
- Structural invariant: `I(W)=C(W)`.
- Structural Representation: `phi(W) in R^23` with group sizes `3,3,3,3,3,3,5`.
- Representation distance: `D_R=||phi(W1)-phi(W2)||_2`.
- Matching: explicit finite/admissible argmin.
- Stage 2E local stability and minimal stability for explicit neighborhoods/subcandidates.
- Stage 2F conditional existence and Stage 2G conditional uniqueness.
- Stage 3 explicit candidate relation domain `C_R`, admissibility predicate `Q`, and exact relation set `R_Q`.

## C. Critical theory ↔ engineering boundaries

### Relation formation is explicit, not heuristic

The frozen graph consumes a supplied relation set. Stage 3 now exposes the
formation boundary as `(C_R, Q, evidence)` and materializes exactly the admitted
pairs. Primitive equality, distance thresholds, connectivity, curvature
thresholds, or hidden neighborhood inference cannot create relations.

### Local stability ≠ global optimality

Stage 2E uses an explicitly supplied perturbation neighborhood. Global selection
remains the separate `argmin` problem over an explicit admissible partition
family.

### Materialization ≠ universal existence

Stage 2F only proves existence conditional on a finite, non-empty admissible
family with finite energy. Stage 2G only proves uniqueness under strict energy
separation.

### Relation formation ≠ a universal geometry-to-relation theorem

Stage 3 deliberately does not invent a geometry formula for `Q`. A future
geometry-derived relation theorem must define `Q` and prove the required
properties before promotion.

## D. Non-negotiable boundaries

1. Legacy energy/partition/primitive inference remains regression baseline code.
2. No hidden threshold may become a mathematical definition.
3. `D_R=0` means equality of supplied 23-D representations only.
4. Deterministic tie-breaking is not uniqueness.
5. `Object`, `Instance`, and `Hierarchy` require their own definitions/proofs.
6. Neural objectives do not prove latent metric equality.
7. Stage 2E neighborhoods/subcandidate families must be explicit inputs.
8. Stage 2F/2G hypotheses must not be promoted to universal claims.
9. Stage 3 candidate pairs and relation predicate must be explicit inputs.
10. Any future contradiction must update the mathematics first or remain legacy/experimental.

## E. Release criterion

The theory-compliant core is regression-clean only when the full
`python -m unittest discover -s tests -v` suite passes and no theory test relies
on legacy heuristics to construct a theory object. Passing tests establish
implementation-contract consistency, not universal existence, uniqueness, or a
universal geometry-to-relation law.
