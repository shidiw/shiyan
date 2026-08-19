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
| `X -> admissible partitions A(X)` | required for genuine structure discovery | `AdmissiblePartitionFamily` represents an externally supplied finite family; construction from `X` remains unfrozen | **BOUNDARY / GAP** |
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

The `AdmissiblePartitionFamily` makes the missing mathematical object explicit: it represents a non-empty finite family `A(X)` supplied from outside the theory-facing core. It enforces that every candidate is a valid partition of the same observation index universe. It does **not** define how `X` generates `A(X)`.

Therefore the implemented contract is now explicit:

`X -> [external construction of A(X)] -> AdmissiblePartitionFamily -> P* -> Units`

The first arrow remains a theory gap. The optimization step is closed for an explicitly supplied finite family:

`P* in argmin_{P in A(X)} E(P)`.

For full closure, the source theory must explicitly define the observation universe, the construction `X -> A(X)`, and existence/selection conditions for the optimization. If the minimizer is not mathematically unique, the theory must remain set-valued or use an explicitly declared deterministic tie-break without calling it uniqueness.

### 3.2 Unit

The theory freezes:

`u_i=(G_i,theta_i)`.

`StructuralUnit` stores support indices as `G_i` and attributes as `theta_i`. Primitive is explicitly optional metadata and is therefore not silently promoted to Unit identity. The legacy positional constructor is compatibility only and materializes the same support/attribute object.

### 3.3 Relation — formal discovery boundary

The current theory-facing relation object is a typed record

`r_ij = (i,j,type,evidence)`

with distinct non-negative endpoints. The engineering implementation validates endpoint/domain integrity and preserves the supplied type and evidence without deriving them from Unit metadata. In particular, equal primitive labels, shared attributes, distance thresholds, connected components, or legacy relation heuristics do not create a Relation in the frozen core.

The current constructor boundary is therefore:

`(u_i,u_j, supplied relation type, supplied evidence) -> r_ij`.

This is **not** yet the mathematical discovery map

`(u_i,u_j,X) -> r_ij`

because the source theory has not frozen the predicates that decide whether a relation exists or which relation type is valid. The engineering API deliberately cannot fill that gap by guessing.

For full closure, each relation type must acquire an explicit mathematical predicate, for example a statement of the form

`R_t(u_i,u_j; X) in {true,false}`

or an equivalent admissibility relation, together with the domain conditions and any required invariance/equivariance properties. The theory must also specify whether relations are directed or undirected, whether multiple relation types may coexist for the same endpoint pair, and whether evidence is mathematical state or merely provenance metadata.

Until those items are frozen, `StructuralRelation` is a **boundary object**, not a relation-discovery theorem.

### 3.4 Relation -> Graph and World

The graph contract is explicit:

`G=(V,E)`

with vertices indexed by world Units and edges copied from the supplied Relation set. No additional edges are generated from attributes or primitive labels.

The World contract is:

`W=(U,R,Phi)`.

The implementation validates relation endpoints against the Unit domain. Thus the implication

`R supplied -> E = R`

is closed, while

`U -> R`

remains a theory gap.

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

The metric regression suite explicitly covers non-negativity, symmetry, zero distance for equal representations, and the triangle inequality in addition to the existing Euclidean-value checks.

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

The user's latest local regression run reports:

`Ran 89 tests ... OK`

The current branch also strengthens the relation boundary regression by explicitly testing construction through supplied relation type/evidence without allowing Unit metadata to determine the relation.

Passing the suite confirms implementation-contract consistency. It does not establish the missing relation-discovery predicates.

## 7. Final mathematical verdict

The downstream algebra is now contract-clean:

`Partition -> Unit -> explicit Relation -> Graph -> World -> Canonical Form -> Invariant -> R^23 representation boundary -> D_R -> Matching -> Neural objective boundary`.

The upstream discovery boundary is now explicit rather than implicit:

`X -> external A(X) -> finite admissible family -> argmin -> Units`.

However, **Struct3D is not yet a fully closed mathematical theory from raw observation to learned structure**. The blockers are explicit and finite in number:

1. **Observation -> admissible partition construction** is not frozen in the source theory.
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
