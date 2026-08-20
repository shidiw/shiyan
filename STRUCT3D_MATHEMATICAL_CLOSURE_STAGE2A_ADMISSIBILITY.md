# Struct3D Mathematical Closure — Stage 2A: Admissibility and Unit Emergence Audit

## Status

This document is a source-grounded supplement to `STRUCT3D_MATHEMATICAL_CLOSURE_STAGE2_AUDIT.md`.

The purpose is to close the **admissibility side** of the upstream chain as far as the preserved theory actually permits. It deliberately does not invent a candidate generator, threshold, connectivity rule, or energy decomposition that is absent from the authoritative material.

## 1. Authoritative chain recovered from the preserved Struct3D documents

The preserved engineering/theory description gives the conceptual chain:

`Geometry -> Measure -> Energy -> Stability -> Unit`

and, at the partition level:

`Observation X -> admissible partitions -> energy minimization -> stable local structure -> Unit`.

It also states the conceptual distinction:

`Unit != Point`, `Unit != Superpoint`, `Unit != Primitive`.

The preserved mathematical theory defines the frozen Unit object as:

`u_i = (G_i, theta_i)`.

It further defines the downstream world as:

`W = (U, R, Phi)`.

Therefore the correct interpretation is that the upstream formation problem must produce valid structural cells before the downstream World representation is constructed.

## 2. What can be frozen now: the admissible-partition interface

Let the finite observation universe be

`X = {1, ..., N}`.

A partition candidate is a finite family

`P = {A_1, ..., A_K}`

such that:

1. `A_i != emptyset` for every `i`;
2. `A_i subseteq X` for every `i`;
3. `A_i intersection A_j = emptyset` whenever `i != j`;
4. `union_i A_i = X`.

The current theory-compliant implementation already enforces these conditions on `Partition` objects. This is therefore a legitimate frozen **partition validity contract**.

Important limitation:

`Partition validity != admissibility`.

A valid partition is only a mathematically well-formed partition. The preserved material does not yet provide a complete predicate saying which valid partitions belong to the admissible family `A(X)`.

## 3. The correct definition boundary for A(X)

The mathematically safe statement is:

`A(X) subseteq Part(X)`

where `Part(X)` denotes the set of all valid finite partitions of `X`.

The selection problem is then:

`P* in argmin_{P in A(X)} E(P)`.

This is already supported by the current theory-facing implementation because the candidate family is explicitly supplied to the selector.

The missing object is the construction rule:

`X -> A(X)`.

No current source justifies replacing this missing rule with any of the following as a theorem:

- Euclidean-radius thresholding;
- curvature thresholding;
- k-nearest-neighbor connectivity;
- graph connected components;
- primitive classification;
- minimum point count;
- a fixed energy threshold;
- a stability score threshold.

Those can remain engineering mechanisms or future hypotheses, but they cannot be silently promoted to the mathematical definition of `A(X)`.

## 4. Candidate generation versus candidate validation

This distinction is now explicit.

### Validation

`validate(P, X)` checks whether a supplied family `P` is a valid partition of `X`.

This is already closed in the current core.

### Generation

`generate_A(X)` would construct the admissible family itself.

This is **not closed**.

The current core must therefore not pretend that partition validation is a discovery algorithm.

The correct engineering boundary remains:

`candidate source -> valid Partition -> theory selector`.

## 5. Energy minimization is downstream of admissibility

For an externally supplied functional `E`, the current theorem-safe operation is:

`P* in argmin_{P in A(X)} E(P)`.

This does not imply that every cell of `P*` is independently an energy-minimizing Unit.

It only says that the selected partition minimizes the supplied partition-level objective over the supplied candidate family.

Therefore the following inference is currently **not justified**:

`P* minimizes E -> every A_i in P* is a Structural Unit theorem`.

A separate Unit-emergence/stability/minimality theorem is still required.

## 6. Stability: what the source supports and what it does not

The historical material describes a stable local structure and links the idea of stability to the cost behavior of structural changes, including splitting. However, the preserved source does not freeze a complete mathematical neighborhood of perturbations nor a unique split/merge inequality.

Consequently the following statements remain hypotheses, not frozen laws:

`Delta E_merge < 0 => merge`;

`Delta E_merge >= 0 => stable Unit`;

`exp(-E(A)) log(|A|+1) > tau => Unit`.

In particular, no universal numeric threshold is part of the frozen theory.

## 7. Minimality is a separate missing condition

A stable region can contain a smaller stable subregion. Therefore stability alone cannot automatically establish that a region is a primitive structural atom.

A mathematically complete Unit-emergence theorem will need a notion of minimality, for example a statement of the form:

`A is stable and contains no proper admissible stable subregion`.

However, the exact notion of "proper", "admissible", and "stable" must be recovered or explicitly derived and frozen before this becomes Struct3D theory.

This document therefore records minimality as a **required closure target**, not as a newly introduced theorem.

## 8. Existence and well-posedness

For a finite non-empty explicit candidate family `A(X)`, a real-valued energy function attains a minimum because the search set is finite.

Thus the implementation can safely establish:

`A(X) != emptyset` and `E: A(X) -> R`

`=> argmin_{P in A(X)} E(P) != emptyset`.

This is an existence statement for the **explicit finite selection problem**.

It is not an existence theorem for a naturally generated admissible family from arbitrary point-cloud observations.

That stronger statement requires a mathematical definition of `A(X)` and assumptions guaranteeing that it is non-empty.

## 9. Engineering correspondence

The current branch now has the following defensible correspondence:

| Mathematical object | Engineering boundary | Status |
|---|---|---|
| Observation universe `X` | finite indexed `Partition.universe` | CLOSED |
| Valid partition `P` | `Partition` validation | CLOSED |
| Admissible family `A(X)` | explicitly supplied candidate partitions | BOUNDARY |
| Candidate generation `X -> A(X)` | no theory-facing generator | THEORY GAP |
| Energy `E` | externally supplied functional | BOUNDARY |
| `argmin E` | explicit finite minimizer | CLOSED |
| Stable candidate | no frozen predicate | THEORY GAP |
| Minimal stable candidate | no frozen predicate | THEORY GAP |
| Structural Unit | `StructuralUnit(G, theta)` | CLOSED as object/materialization boundary |
| World | `StructuralWorld(U,R,Phi)` | CLOSED |

## 10. Required next theorem package

The next mathematical closure should not add arbitrary code first. It should establish, in this order:

### A1. Admissibility definition

A precise predicate `Adm(A; X)` and therefore:

`A(X) = { A : Adm(A; X) }`.

### A2. Energy domain

A precise functional:

`E : A(X) -> R`.

If the historical additive skeleton is retained, the exact definitions of its terms must be supplied before implementation.

### A3. Stability definition

A precise admissible perturbation/splitting family `N(A)` and a predicate `Stable(A)`.

### A4. Minimality definition

A predicate `Minimal(A)` that prevents a stable candidate from containing a proper stable subcandidate.

### A5. Unit emergence theorem

A theorem connecting the previous definitions to the frozen Unit object, rather than merely asserting that low energy means Unit.

### A6. Existence theorem

Assumptions on `X`, `A(X)`, and `E` under which at least one selected stable/minimal candidate exists.

## 11. Release decision

**Stage 2A is closed only for the partition-validity boundary, not for admissible candidate generation.**

The correct current mathematical pipeline is therefore:

`X`

`-> explicit admissible candidate family A(X)`  [boundary]

`-> finite argmin of supplied E`  [closed]

`-> valid partition cells`  [closed]

`-> Structural Units`  [materialization boundary]

`-> Structural World`  [closed]

The missing upstream mathematical links remain:

`X -> A(X)`;

`stable/minimal candidate -> Unit`.

No implementation should fill these gaps by silently importing legacy thresholds or primitive heuristics.

## 12. Audit conclusion

The most important correction from this stage is that **candidate generation, partition validity, energy minimization, stability, and Unit emergence are five different mathematical responsibilities**.

The current branch correctly closes the second and supports the fourth only as an explicit optimization boundary. It must not claim that the existing code has already solved the first, third, or fifth.

This preserves the integrity of the Struct3D theory-to-code comparison and gives the next stage a precise target: recover/freeze `Adm`, the exact energy functional, stability, and minimality before adding a theory-facing discovery algorithm.
