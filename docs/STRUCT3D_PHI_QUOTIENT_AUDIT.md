# Struct3D Phi Quotient-Space Audit

## Verdict

The World quotient is now frozen as an index-free finite object `C_Q(W)`, and
`I(W)=C_Q(W)` is the theory-facing invariant.

Therefore the theory-level construction

`Phi_Q([W]) = F(C_Q(W))`

is well-defined for every explicitly supplied finite extractor `F`.

This is a **well-definedness theorem**, not an injectivity or semantic
completeness theorem.

## Raw-world boundary

`structure/theory_representation.py::represent(world, extractor)` remains an
intentional low-level boundary. It accepts arbitrary raw-world extractors and
therefore does not certify quotient invariance.

A raw extractor `F(W)` is quotient-compatible exactly when

`W1 ~_W W2 => F(W1)=F(W2)`.

The regression helper `phi_well_defined_on_quotient` checks this property over a
finite test family.

## Frozen quotient path

`represent_canonical` now receives `structural_invariant(W)`, and
`structural_invariant(W)` is the new index-free `C_Q(W)`.

Thus raw support indices cannot enter the theory-facing representation through
this path.

## Legacy v4.0 audit

The legacy `experiments/v40/run_v40_structural_representation.py` computes a
23-dimensional vector from primitive/object/relation histograms, relation
confidence statistics, object-size statistics, and instance occupancy. Those
statistics are largely label-order insensitive, but this file is an experiment
and is **not** the frozen theory representation implementation.

More importantly, its coordinate partition is

`5 + 4 + 5 + 3 + 3 + 3 = 23`,

while the frozen theory schema currently declares

`3 + 3 + 3 + 3 + 3 + 3 + 5 = 23`.

Therefore the legacy v4.0 numerical vector cannot be promoted as the frozen
`Phi` without an explicit mathematical reconciliation of the coordinate schema.

## Remaining mathematical task

The quotient-space well-definedness problem is closed.

The remaining v4.0 theorem is now sharply isolated:

1. freeze the seven numerical coordinate maps `Phi_1,...,Phi_7` on `C_Q(W)`;
2. prove each coordinate is finite and quotient-compatible;
3. prove the resulting map lands in the declared `R^23` schema;
4. separately establish whatever injectivity/information-separation property is
   actually required for `D_R`.

No neural network is needed for this closure step.
