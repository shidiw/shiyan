# Struct3D Mathematical Closure — Stage 1

## Scope

This audit closes **the audit of the upstream chain**, not the missing mathematics itself:

`Observation X -> admissible partition family A(X) -> energy minimization -> partition P* -> Structural Units U`.

The historical mathematical document is authoritative for this audit. Later v3.x/v4.0 definitions are not used to invent missing v0.x mathematics.

## 1. Historical statements recovered

The preserved Struct3D theory states the following early chain:

`Geometry -> Energy landscape -> Stable region -> Unit`.

It also records the early energy form

`E = E_fit + lambda_c C + lambda_b B`,

where `E_fit` is geometric fitting error, `C` is an internal inconsistency / compatibility cost, and `B` is a boundary cost.

The historical text further states that a candidate region becomes a structural unit when its internal geometry is coherent and splitting increases the overall structural cost. However, the exact admissibility predicate and the exact split/merge inequality are not preserved in the current authoritative theory file.

## 2. Current frozen engineering implementation

The theory-facing core deliberately does **not** manufacture `A(X)` or a unique energy functional.

- `structure/theory_core.py` represents a finite valid partition explicitly.
- `select_minimizer(candidates, functional)` computes an argmin over an explicitly supplied admissible finite set.
- `structure/theory_materialization.py` materializes already-valid partition cells as Units by identity.
- No thresholding, primitive fitting, clustering, graph connected-components rule, or legacy energy implementation is silently promoted into the frozen theory.

This is mathematically conservative and is the correct boundary until the missing definitions are recovered or explicitly derived.

## 3. Legacy energy comparison

`structure/energy.py` contains the historical implementation

`E_legacy = E_fit + lambda * E_complexity + gamma * E_boundary`.

Its implementation details include primitive-specific fitting, primitive-parameter complexity dimensions, and a centroid/radius-variance boundary surrogate.

Therefore the following identification is **not currently justified**:

`C == E_complexity` and `B == E_boundary`.

The implementation is a regression baseline, not the definition of the frozen mathematical functional.

## 4. Exact mathematical closure status

### CLOSED

1. Observation universe can be represented as a finite indexed set.
2. A valid partition is non-empty, pairwise disjoint, and complete over its universe.
3. A Structural Unit is `u=(G, theta)`.
4. Given an explicit admissible candidate family and an externally supplied scalar functional, an optimal candidate can be selected by argmin.
5. Materialization of an already-valid partition into Units is identity-preserving.

### BOUNDARY

`A(X)` is an explicit external input to the frozen core. The core does not claim that it has discovered the candidate family from raw observations.

### THEORY GAP

The following historical claims still lack a frozen exact definition/proof in the current theory:

1. **Admissible partition operator:** a precise definition of `A(X)`.
2. **Structural energy:** an exact mathematical definition of `E` matching the preserved historical `E_fit + lambda_c C + lambda_b B` form.
3. **Emergence/stability predicate:** a precise condition under which a candidate region is a stable Unit, including the preserved idea that splitting should increase total structural cost.
4. **Existence/selection conditions:** conditions ensuring the admissible family is non-empty and the minimization problem is well-posed.
5. **Minimality:** a formal definition of what makes an emergent Unit “minimal”.

## 5. Non-negotiable conclusion

Do **not** convert any of the following legacy engineering choices into mathematics merely to close the chain:

- curvature thresholds;
- spatial-distance thresholds;
- minimum point counts;
- connected-component extraction;
- plane/sphere/cylinder classifier;
- primitive parameter-count complexity;
- centroid/radius-variance boundary surrogate.

Those are implementation choices unless the mathematical specification explicitly defines and proves them.

## 6. Required next mathematical step

The next closure target is **not code invention**. It is recovery/formalization of the missing historical definition of the admissible family and stability condition:

`X -> A(X)`

and then

`P* in argmin_{P in A(X)} E(P)`.

Only after those are mathematically frozen should the engineering implementation be changed to realize them.

## 7. Audit verdict

**Stage 1 result: upstream chain audited; not falsely declared mathematically closed.**

The current 90-test regression suite validates the frozen engineering contracts, but it cannot by itself establish the missing `A(X)`, exact energy, or emergence theorem.
