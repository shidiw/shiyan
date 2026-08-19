# Struct3D Mathematical Closure Audit

Branch: `refactor/theory-compliant-core`

## 1. Audit principle

`Struct3D_数学理论.txt` is authoritative. Engineering code must not silently turn a legacy heuristic into a mathematical definition. `Struct3D_工程实现.txt` and historical modules are evidence of implementation history, not automatic theory.

Audit states:

- **CLOSED**: the mathematical object is defined and the theory-facing implementation matches it.
- **BOUNDARY**: the interface exists, but the mathematical construction is intentionally supplied externally.
- **GAP**: the theory requires a construction/theorem that is not yet fully frozen.
- **LEGACY**: historical implementation retained only for regression comparison.

## 2. End-to-end closure map

| Stage | Mathematical contract | Current implementation | Status |
|---|---|---|---|
| Observation `X` | raw observation/input | legacy geometry/data code exists | LEGACY INPUT |
| `X -> admissible partitions A(X)` | required for genuine structure discovery | no frozen construction | **GAP** |
| Partition | finite, nonempty, disjoint, complete cover | `structure/theory_core.py::Partition` | **CLOSED** |
| Partition -> Unit | materialize partition cells without changing them | `theory_materialization.py` identity materialization | **CLOSED AS EXTERNAL BOUNDARY** |
| Unit | `u=(G,theta)` | single `StructuralUnit` type | **CLOSED** |
| Unit -> Relation | relation from frozen structural predicate | explicit typed relation + evidence; no inference | **BOUNDARY / GAP** |
| Relation -> Graph | `G=(V,E)`, explicit `E` | graph copies supplied relations exactly | **CLOSED** |
| World | `W=(U,R,Phi)` | `StructuralWorld` | **CLOSED** |
| Relabeling | legal permutation of Unit labels | finite permutation semantics used by canonicalization | **CLOSED FOR FINITE REGIME** |
| Canonical form | `C(W)=C(pi(W))` | exhaustive finite canonicalization | **CLOSED FOR FINITE REGIME** |
| Structural equivalence | canonical equality in the implemented finite representation | `structurally_equivalent(a,b)` | **CLOSED AS IMPLEMENTED** |
| Invariant | `I(W)=I(pi(W))`; frozen choice `I(W)=C(W)` | explicit invariant layer | **CLOSED** |
| Representation | `phi(W) in R^23` | 23-D schema + explicit extractor boundary | **BOUNDARY** |
| Representation invariance | requires properties of the actual extractor | arbitrary extractor is not certified | **GAP/BOUNDARY** |
| Distance | `D_R=||phi(W1)-phi(W2)||_2` | Euclidean implementation | **CLOSED** |
| Distance axioms | non-negativity, symmetry, identity in representation space, triangle inequality | distance implementation + regression coverage | **CLOSED** |
| Matching | `argmin_{M in A} C(M)` | explicit finite candidate set + supplied cost | **CLOSED** |
| Neural reconstruction | `z=f_theta(phi(W))` + explicit objective | neural objective contract | **CLOSED AS TRAINING CONTRACT** |
| Latent metric preservation | `D_Z approx D_R` | not proved | **GAP** |

## 3. Stage-by-stage audit

### 3.1 Observation -> Partition / Unit

This is the first genuine mathematical hole. The frozen implementation intentionally does not pretend that legacy thresholding, connected components, primitive fitting, minimum-size filtering, or legacy energy automatically define Struct3D Units.

The current `Partition` object validates a **supplied** finite partition. Therefore the implemented contract is:

`P in admissible input -> materialized Units`

not yet:

`X -> A(X) -> P* -> Units`.

For full closure, the theory must explicitly define the observation universe, admissible partition family `A(X)`, and existence/selection conditions for the optimization. If the minimizer is not mathematically unique, the theory must remain set-valued or use an explicitly declared deterministic tie-break without calling it uniqueness.

### 3.2 Unit

The theory freezes:

`u_i=(G_i,theta_i)`.

`StructuralUnit` stores support indices as `G_i` and attributes as `theta_i`. Primitive is explicitly optional metadata and is therefore not silently promoted to Unit identity. The legacy positional constructor is compatibility only and materializes the same support/attribute object.

### 3.3 Relation

The theory defines a relation between Units and states that its evidence may involve geometry, boundary and spatial configuration. The engineering implementation correctly refuses to infer relations from primitive equality or an unapproved threshold. It accepts an explicit relation type/evidence record.

This is mathematically safe but not yet a discovery theorem. Full closure requires frozen predicates for relation types and their admissibility/invariance properties.

### 3.4 Graph and World

The graph contract is explicit:

`G=(V,E)`

with vertices indexed by world Units and edges copied from the supplied Relation set. No additional edges are generated from attributes or primitive labels.

The World contract is:

`W=(U,R,Phi)`.

The implementation validates relation endpoints against the Unit domain.

### 3.5 Canonical Structural Form

The implementation enumerates all finite Unit relabelings and chooses the lexicographically minimal serialization. This is an exact finite definition for the validation regime, not a scalable canonical-labeling algorithm.

Important limitation: the canonicalization claim is only as strong as the serialization of the frozen world fields. The implementation includes Unit support, primitive metadata, attributes, relation endpoints/types/evidence, and world attributes. It does not introduce an extra graph hash or heuristic.

### 3.6 Structural Invariant

The frozen implementation uses:

`I(W)=C(W)`.

The invariant layer therefore does not invent a second numerical invariant. Relabeling invariance is inherited from the exact finite canonical form.

### 3.7 23-D Representation

The theory freezes:

`phi(W) in R^23`

with groups:

`3+3+3+3+3+3+5=23`.

The engineering schema enforces exactly 23 finite real coordinates and the seven group boundaries. It deliberately does not invent numerical formulas for the seven groups. Consequently, the extractor remains an explicit boundary until the coordinate formulas are mathematically frozen.

No claim is permitted that an arbitrary extractor is invariant, injective, complete, or uniquely determined by the 23-D schema.

### 3.8 Structural Distance

The implementation is exactly the frozen representation-space Euclidean distance:

`D_R(W1,W2)=||phi(W1)-phi(W2)||_2`.

The correct identity statement is:

`D_R(W1,W2)=0 <=> phi(W1)=phi(W2)`.

It is **not** structural identity unless injectivity of `phi` on the intended structural quotient is separately proved.

The metric regression suite now explicitly covers non-negativity, symmetry, zero distance for equal representations, and the triangle inequality in addition to the existing Euclidean-value checks.

### 3.9 Structural Matching

Matching is implemented as minimization of a supplied cost over an explicit admissible candidate set. Empty candidate sets and non-finite costs are rejected. Stable tie selection is deterministic but is not described as a uniqueness theorem.

### 3.10 Neural Struct3D

The current neural layer is correctly restricted to an objective/training contract. Reconstruction does not imply latent metric preservation.

The unresolved research statement is:

`D_Z(f_theta(phi(W1)), f_theta(phi(W2))) approx D_R(W1,W2)`.

The earlier large latent-distance error must remain evidence of an unresolved empirical problem, not be relabeled as a theorem failure or theorem success.

## 4. Legacy containment audit

The following historical mechanisms remain outside the frozen theory core:

- primitive fitting;
- thresholded graph construction;
- minimum-point filtering;
- legacy primitive energy;
- historical relation inference;
- memory/prototype engineering modules;
- unproved Instance promotion;
- unproved Hierarchy promotion.

Their regression tests preserve behavior for historical code. Passing those tests does not establish the corresponding mathematics.

## 5. Instance / Hierarchy / Object boundary

The current code deliberately does not promote Instance or Hierarchy into the frozen mathematical core. Object assembly is explicitly marked as a derived engineering construction. This is the correct boundary until definitions and invariance theorems are frozen.

Therefore the chain is **not** allowed to become:

`Unit -> Object -> Instance -> Hierarchy`

merely because those names existed in historical engineering code.

## 6. Test audit

The user-provided local regression run reports:

`Ran 81 tests ... OK`

This confirms that the existing 81-test contract suite is clean at the current local checkout.

An additional test module, `tests/test_theory_distance_axioms.py`, has now been added to the branch to cover the explicit metric axioms that were previously under-tested:

- non-negativity;
- symmetry;
- triangle inequality;
- zero distance for equal representations.

Because this additional module was committed after the user's 81-test run, the post-change total must be re-run locally. No claim is made that the new total has already been executed in the user's checkout.

Recommended verification command:

`python -m unittest discover -s tests -v`

## 7. Final mathematical verdict

The downstream algebra is now contract-clean:

`Partition -> Unit -> explicit Relation -> Graph -> World -> Canonical Form -> Invariant -> R^23 representation boundary -> D_R -> Matching -> Neural objective boundary`.

However, **Struct3D is not yet a fully closed mathematical theory from raw observation to learned structure**. The blockers are explicit and finite in number:

1. **Observation -> admissible partition/unit construction** is not frozen.
2. **Unit -> relation discovery** is not frozen as a formal predicate/theorem.
3. **The numerical 23-D extractor `phi`** is a schema plus external mapping, not a fully derived coordinate theorem.
4. **Latent distance preservation** is not a theorem and must remain an empirical research target.

Everything else currently represented in the frozen core must remain within these boundaries.

## 8. No-go rules for the next implementation stage

Do not:

- import legacy primitive energy into the theory-facing Unit definition;
- turn a threshold into a definition of relation or Unit;
- turn connected components into a theorem without first freezing the admissible relation/partition construction;
- claim `D_R=0` means structural equivalence without representation injectivity;
- claim arbitrary 23-D statistics are mathematically derived coordinates;
- claim reconstruction proves latent metric preservation;
- promote Object, Instance, or Hierarchy without explicit mathematical definitions and invariance proofs.

This document is an audit artifact. It does not replace `Struct3D_数学理论.txt` and does not introduce new mathematical definitions into the frozen theory.
