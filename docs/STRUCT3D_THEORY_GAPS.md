# Struct3D theory-to-code gap register

This document is a boundary register, not a new mathematical theory.

## Frozen by the supplied mathematical specification

- Structural Unit: `u_i = (G_i, theta_i)`.
- Structural World: `W = (U, R, Phi)`.
- Structural Graph: `G = (V, E)` with units as vertices and explicit relations as edges.
- Relabeling invariance / canonicalization / invariant representation are later structural requirements.
- v4.0 freezes the 23-dimensional structural representation used by the current neural stage.

## Not frozen by the supplied specification

### 1. Raw observation -> admissible partitions

The specification does not provide a unique operator

`A(X) -> {Pi}`

that constructs the admissible partition family from a raw point cloud.

Current code therefore treats `Partition` as a validity container and accepts
candidate partitions externally. Legacy thresholding, connected components,
minimum-size filtering, or primitive labels are not theory-level definitions.

### 2. Energy functional

The specification does not freeze a unique scalar functional `E(Pi)`.

Consequently `evaluate_energy()` accepts an explicit functional. Historical
`structure/energy.py` remains a legacy implementation and is not silently
promoted into the theory.

### 3. Unit discovery theorem

Because (1) and (2) are not frozen, the implementation must not claim the
strong statement

`Pi* = argmin_{Pi in A(X)} E(Pi)`

as an established Struct3D theorem. The current `select_minimizer()` is only
a generic finite-set optimization operator.

### 4. Relation construction

The mathematical object `R` is frozen, but a unique executable constructor
from geometry and boundaries to every relation is not frozen. Relation
instances therefore require explicit type/evidence; primitive-type equality
cannot manufacture relations.

### 5. Object / Instance / Hierarchy

The engineering history contains these layers, but their existence in the
historical code list does not by itself make them foundational mathematical
definitions. They remain derived/provisional until their formal definitions
are explicitly frozen.

## Engineering rule

No item in this register may be promoted into the mathematical Core merely
because a legacy implementation exists. A future promotion requires either:

1. an explicit mathematical definition in the specification, or
2. an explicit, reviewed decision to extend the theory.
