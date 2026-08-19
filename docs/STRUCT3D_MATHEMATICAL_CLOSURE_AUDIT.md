# Struct3D Mathematical Closure Audit

Branch: `refactor/theory-compliant-core`

## 1. Audit principle

`Struct3D_数学理论.txt` is authoritative. Engineering code must not silently turn a legacy heuristic into a mathematical definition.

This audit distinguishes four states:

- **Closed**: the mathematical object is defined and the theory-facing implementation matches it.
- **Boundary**: the engineering interface exists, but the mathematical construction is intentionally supplied externally.
- **Gap**: the theory names or requires a construction, but no complete definition/theorem is frozen.
- **Legacy**: historical implementation retained for regression comparison only.

## 2. Current closure map

| Chain | Theory statement | Engineering status | Audit result |
|---|---|---|---|
| Observation -> World | `X -> W` | No frozen construction from raw observations | **GAP** |
| Observation -> Partition | admissible partition is needed before Unit materialization | `Partition` validates a supplied finite partition | **BOUNDARY** |
| Partition -> Unit | a valid partition already contains Unit cells | `materialize_units()` is identity | **CLOSED AS BOUNDARY** |
| Unit | `u=(G,theta)` | `StructuralUnit` | **CLOSED** |
| Unit -> Relation | relation may depend on geometry/boundary/spatial evidence | typed relation record only; no inference | **BOUNDARY / GAP** |
| Relation -> Graph | `G=(V,E)` with explicit relations | theory graph copies supplied relations | **CLOSED** |
| Units + Relations + Attributes -> World | `W=(U,R,Phi)` | `StructuralWorld` | **CLOSED** |
| World -> Canonical Form | `C(W)=C(pi(W))` | finite exact canonicalization | **CLOSED for finite validation regime** |
| Canonical Form -> Invariant | `I(W)=C(W)` | explicit invariant layer | **CLOSED** |
| World -> 23-D representation | `phi(W) in R^23` | extractor boundary + schema | **BOUNDARY** |
| Representation -> Distance | `D_R=||phi(W1)-phi(W2)||_2` | Euclidean distance | **CLOSED** |
| Matching | `argmin` over explicit admissible set | explicit finite argmin | **CLOSED** |
| Neural reconstruction | `z=f_theta(phi(W))` with reconstruction objective | objective boundary | **CLOSED AS TRAINING CONTRACT** |
| Latent metric preservation | `D_Z approx D_R` | not a theorem | **GAP** |

## 3. First unresolved closure: Observation -> Unit

The current frozen implementation deliberately does **not** claim to derive a Structural Unit from raw point observations. `Partition` is an externally supplied valid finite partition, and `materialize_units()` only exposes its cells. This prevents thresholds, connected components, primitive fitting, or legacy energy from being promoted into the theory.

Therefore the missing mathematical object is an explicit admissible-family construction such as:

`X -> A(X)` where `A(X)` is a mathematically defined set of admissible partitions.

Only after that is defined can the existing argmin contract

`P* in argmin_{P in A(X)} E(P)`

become a genuine observation-to-structure construction rather than an abstract optimization interface.

**Required before closure:** definition of the observation universe, admissible partition family, and conditions under which the minimizer exists. If uniqueness is not proved, the result must remain set-valued or use a declared deterministic tie-break without claiming uniqueness.

## 4. Second unresolved closure: Unit -> Relation

The theory text states that structural relations are associated with geometry, boundary and spatial configuration. The current theory-facing implementation intentionally accepts an explicit relation type and evidence and rejects heuristic inference. This is correct as a boundary, but it is not yet a relation-discovery theorem.

The missing mathematical object is a relation operator, for example in abstract form:

`R_X(U) = { r_ij : Q(U_i,U_j; geometry,boundary,spatial evidence) satisfies the frozen relation definition }`.

The exact predicate/type definitions are **not** to be invented by the engineering layer.

**Required before closure:** formal relation predicates, admissibility conditions, invariance under legal relabeling, and a proof that the relation construction is well-defined on the intended structural objects.

## 5. Third unresolved closure: 23-D coordinates

The theory freezes the dimension and seven coordinate groups, but the engineering boundary correctly does not invent a numerical feature extractor. Therefore `phi: W -> R^23` is currently an explicit supplied mapping, not a fully derived theorem.

The following must not be claimed without additional mathematics:

- arbitrary statistics are not automatically coordinates of `phi`;
- `phi(W1)=phi(W2)` does not imply structural equivalence;
- `D_R=0` does not imply `W1 ~= W2` without injectivity on the relevant quotient;
- relabeling invariance of an arbitrary supplied extractor is not automatic.

## 6. Fourth unresolved closure: neural metric geometry

The reconstruction objective is not a proof that latent Euclidean distance equals structural representation distance. The previously observed large relative-distance error is evidence that reconstruction alone is insufficient. A future distance-preserving objective may be implemented experimentally, but it must not be promoted to a theorem until the corresponding mathematical statement and validation protocol are fixed.

## 7. Legacy-code containment audit

The following historical mechanisms remain outside the frozen mathematical core:

- primitive fitting;
- thresholded graph clustering;
- minimum-point filtering;
- legacy primitive energy;
- legacy relation inference;
- historical memory/prototype code;
- unproved Instance/Hierarchy promotion.

Their tests are regression tests, not evidence that the corresponding mathematical theory is complete.

## 8. Closure criterion

The mathematical chain is considered fully closed only when every arrow required by the stated theory has either:

1. a formal definition and matching implementation; or
2. an explicitly documented external input boundary that the theory itself declares to be supplied.

At the current checkpoint, the downstream structural algebra from supplied Units/Relations through World, canonicalization, invariant, representation boundary, representation distance, and matching is contract-clean. The two principal upstream construction gaps are **Observation -> admissible Unit/Partition** and **Unit -> mathematically defined Relation**. The 23-D extractor and neural metric preservation remain intentionally explicit research boundaries.

This document is an audit artifact, not a replacement for `Struct3D_数学理论.txt` and does not introduce new mathematical definitions into the frozen theory.
