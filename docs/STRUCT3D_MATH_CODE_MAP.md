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
| v0.5 Structural Unit Discovery | A mathematically defined discovery operator | `structure/theory_materialization.py` | **Boundary only**; materialization is identity on an already valid partition; discovery is not silently invented |
| v0.6 Primitive Discovery | Primitive inference from geometry | legacy primitive modules | **Theory gap; intentionally not implemented in the frozen core** |
| v0.7 Primitive Energy | A frozen mathematical primitive energy functional | legacy `structure/energy.py` | **Theory gap**; legacy energy remains a regression baseline and is not the definition of Unit Energy |
| v0.8 Hierarchy + Relation | Explicit Relations; higher hierarchy | `structure/theory_relation.py`, `structure/theory_world.py` | **Relation implemented; hierarchy intentionally not promoted** |
| v0.9 Memory + Prototype | Structural memory/prototype theory | legacy memory/prototype modules | **Theory gap; intentionally not implemented** |
| v1.0 Structural World | `W=(U,R,Phi)` | `structure/theory_world.py` | **Implemented** |
| v1.x Unit | `u_i=(G_i,theta_i)` | `structure/theory_unit.py::StructuralUnit` | **Implemented** as the single frozen Unit type |
| v2.x Assembly / Object | Object emerges from explicitly defined assembly relations | `structure/theory_object.py` | **Derived engineering construction only**; not a frozen theorem |
| v2.x Instance | Instance identity and its mathematical invariance | — | **Theory gap; intentionally not implemented** |
| v2.x Hierarchy | Hierarchical structural object | — | **Theory gap; intentionally not implemented** |
| v3.1–v3.5 equivalence/isomorphism/quotient | Structural equivalence machinery | `structure/theory_canonical.py` | **Finite canonical boundary implemented**; no unproved stronger quotient theorem |
| v3.6 Canonical Structural Form | `C: W -> C`, invariant under legal relabeling | `structure/theory_canonical.py` | **Implemented** by exact finite exhaustive canonicalization |
| v3.7 Structural Invariant | `I(W)=I(pi(W))`; frozen finite choice `I(W)=C(W)` | `structure/theory_invariant.py` | **Implemented**; no second unsupported numerical invariant |
| v3.8 Structural Distance | `D_R(W1,W2)=||phi(W1)-phi(W2)||_2` | `structure/theory_distance.py` | **Implemented** as representation-space Euclidean distance |
| v3.9 Structural Matching | `M* in argmin_{M in A} C(M)` | `structure/theory_matching.py` | **Implemented** over an explicit admissible set and supplied cost |
| v4.0 Structural Representation | `phi(W) in R^23` | `structure/theory_representation.py`, `structure/theory_representation_schema.py` | **Schema and canonical interface implemented**; the theory freezes grouping/dimension, not an unsupported feature extractor formula |
| Neural Struct3D v1.0 | `z=f_theta(phi(W))`, reconstruction objective | `structure/theory_neural_objective.py` and neural code | **Objective/validation boundary only**; latent metric equality is not claimed |
| Distance-preserving neural extension | `D_Z approx D_R` and distance-preserving loss | future neural implementation | **Not yet a theorem or completed algorithm** |

## B. Frozen mathematical objects

The frozen core currently implements the following objects without adding
unstated assumptions:

- Structural Unit: `u=(G,theta)`.
- Explicit Relation: `r=(source,target,type,evidence)`.
- Structural Graph: `G=(V,E)` with `V` indexed by world Units and `E` copied exactly from Relations.
- Structural World: `W=(U,R,Phi)`.
- Canonical form: exact finite `C(W)`.
- **Structural invariant `I(W)=C(W)`.**
- Structural Representation: `phi(W) in R^23` with group sizes `3,3,3,3,3,3,5`.
- Representation distance: `D_R=||phi(W1)-phi(W2)||_2`.
- Matching: explicit finite/admissible argmin.

## C. Critical theory ↔ engineering mismatches that are now explicitly closed

### 1. Primitive ≠ Unit

Legacy code can recognize plane/sphere/cylinder primitives, but the frozen
Structural Unit does not require a primitive label. `primitive` is optional
metadata. Therefore primitive classification cannot silently define Unit
identity.

### 2. Legacy Energy ≠ frozen mathematical Energy

`structure/energy.py` contains the historical engineering energy model and is
kept for regression tests. It is **not** imported as the definition of the
abstract energy functional. The theory-facing energy API accepts the supplied
functional explicitly.

### 3. Relation ≠ inferred edge

The frozen graph maps the supplied relation set exactly. It does not infer an
edge merely because two Units share a primitive, attribute, or other heuristic.
A future relation-discovery theorem must provide its own definition and proof.

### 4. Object / Instance / Hierarchy are not silently promoted

The historical engineering roadmap contains these concepts, but the current
frozen theory only promotes Object as a derived engineering construction. A
mathematical definition and invariance theorem are still required before
Instance or Hierarchy become part of the frozen core. These layers **must not be
promoted into the frozen theory** merely because legacy code or documentation
uses the names.

### 5. Canonical form is finite and exact, not a heuristic hash

The current implementation enumerates finite Unit relabelings and selects the
lexicographically minimal serialization. This is an exact definition for the
finite validation regime; it is not a scalable canonical-labeling algorithm.

### 6. Representation is a 23-D contract, not an invented feature extractor

The theory freezes `phi(W) in R^23` and the seven coordinate groups. It does not
license arbitrary statistics to be presented as mathematically derived
coordinates. The extractor is therefore an explicit boundary.

### 7. `D_R=0` is not structural identity

`D_R=0` proves `phi(W1)=phi(W2)`. It does **not** prove `W1` and `W2` are
structurally equivalent unless injectivity of `phi` on the relevant quotient is
separately established.

### 8. Neural reconstruction is not metric preservation

The reconstruction objective may make `phi_hat` close to `phi`, but it does not
prove `||z1-z2||_2 = D_R(W1,W2)`. That property requires an explicit distance
objective and independent validation. A distance result or a low empirical
error must not be reported as a proof of the mathematical equality. The
historical 53.18% relative-distance error is therefore treated as evidence of
an unresolved research problem, not as a theorem failure hidden by the
implementation.

## D. Non-negotiable boundaries

1. Legacy `structure/energy.py`, legacy partition discovery, and primitive
   fitting remain regression baselines; they are not imports into the frozen
   theory core.
2. No curvature threshold, distance threshold, minimum-size filter, or
   primitive classifier may silently become a mathematical definition.
3. `D_R=0` means equality of the supplied 23-D representations only.
4. A deterministic tie-break does not establish mathematical uniqueness.
5. `Object`, `Instance`, and `Hierarchy` must not be promoted into the frozen
   theory without explicit definitions and proofs.
6. Neural objectives are training contracts, not proofs of latent geometry; they
   must not be reported as a proof of latent metric equality.
7. Any future implementation that contradicts this table must either update the
   mathematics first or remain explicitly marked as legacy/experimental.

## E. Release criterion

The theory-compliant core is regression-clean only when the full
`python -m unittest discover -s tests -v` suite passes and no theory test relies
on legacy heuristics to construct a theory object.

The pre-fix checkpoint reported by the current branch was **81 tests, 77 passed,
4 failed**. The four failures were contract-wording checks and the legacy
positional `StructuralUnit` materialization contract. After the corresponding
code/documentation fixes, this release gate should be rerun locally before the
branch is considered clean. A passing suite establishes
implementation-contract consistency; it does not establish the unresolved
mathematical gaps listed above.
