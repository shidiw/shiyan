# Struct3D upstream mathematical chain status

## Closed boundary

The former open boundary

`X -> A(X) -> Unit`

is now instantiated by Stage 2H for finite observations.

### Definition

For finite non-empty

`X = {x_1, ..., x_n}`,

define

`A(X) = {u_S : empty != S subseteq X}`.

The family therefore contains exactly

`2^n - 1`

candidates and is finite and non-empty.

### Energy selection

For a finite real-valued structural energy `E` on `A(X)`, define

`Stable_X = argmin_{u in A(X)} E(u)`.

Stage 2E stability is instantiated against every competing candidate.

### Unit emergence

Define

`EmergentUnit_X = {u in Stable_X : no proper subcandidate of u belongs to Stable_X}`.

Because `Stable_X` is finite and non-empty, an inclusion-minimal stable candidate
exists. Therefore

`EmergentUnit_X != emptyset`.

A deterministic representative may be selected for engineering execution, but
that does not assert mathematical uniqueness.

## What remains open

This theorem closes **existence of an emergent support Unit**, not semantic
adequacy of the energy. The following are separate obligations:

1. prove or freeze the concrete structural energy model;
2. prove the required invariance of that energy under legal relabeling and
   observation transformations;
3. establish when an emergent support corresponds to a geometrically meaningful
   object rather than merely being an energy minimizer;
4. extend the support-level theorem to a complete partition/object hierarchy.

No hidden geometric threshold is allowed to enter `A(X)` to answer these
questions.

## Engineering implementation

- `structure/theory_unit_emergence.py`
- `tests/test_theory_unit_emergence.py`
- `structure/STRUCT3D_MATHEMATICAL_CLOSURE_STAGE2H.md`

## Formal verdict

**The upstream existence boundary is closed for finite observations. The next
mathematical bottleneck is no longer candidate existence; it is proving that the
chosen structural energy selects semantically correct Units and that the
resulting Unit family composes into the intended structural partition.**
