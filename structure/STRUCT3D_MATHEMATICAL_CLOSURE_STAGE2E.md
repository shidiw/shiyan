# Struct3D Mathematical Closure — Stage 2E

## Scope

Stage 2E closes the **formation boundary** between a stable candidate and the frozen `StructuralUnit` object.

The key rule is that stability and Unit materialization are related but distinct predicates. The implementation must not silently invent a merge threshold, point-count threshold, primitive classifier, connectivity rule, or global existence/uniqueness theorem.

## 1. Frozen Unit definition

A Structural Unit remains

`u = (G, theta)`

implemented by `structure/theory_unit.py::StructuralUnit`.

Primitive labels remain optional metadata and do not define Unit identity.

## 2. Stability predicate

For an explicitly supplied candidate `u`, an explicitly supplied neighborhood `N(u)`, and a finite scalar energy `E`, define

`Stable(u; N, E) <=> E(u) <= E(v) for every v in N(u)`.

This is a local minimum predicate relative to the supplied perturbation family.

The neighborhood is part of the mathematical input. The frozen core does not infer it from geometry.

## 3. Minimal-stable predicate

Let `S(u)` be an explicitly supplied family of proper subcandidates. Define

`MinimalStable(u) <=> Stable(u) and no v in S(u) is Stable(v)`.

This is relative minimality. It does not claim that the candidate is globally minimal over all possible subsets or partitions.

The proper-subcandidate family is explicit because the historical theory does not preserve a unique splitting operator.

## 4. Unit materialization

Stage 2E defines the engineering formation boundary as

`Materializable(u) <=> Stable(u) and MinimalStable(u)`.

When this predicate is true, the candidate is materialized as the single frozen `StructuralUnit` object without changing its support or attributes.

When false, materialization is rejected explicitly.

## 5. What Stage 2E does NOT prove

Stage 2E does not prove any of the following:

1. that a stable candidate exists for every observation;
2. that a stable candidate is unique;
3. that the local minimum is a global minimum;
4. that a particular geometric merge rule is universally valid;
5. that the historical primitive-energy implementation is the unique mathematical energy;
6. that observation invariance of the resulting Unit has already been proved.

These require separate mathematical statements and hypotheses.

## 6. Closed logical chain so far

The theory-facing pipeline is now explicitly separated as

`X -> explicit admissible candidates -> explicit energy -> stability neighborhood -> Stable -> MinimalStable -> Materializable StructuralUnit`.

The `argmin` operator remains the separate global-selection mechanism over an explicit admissible partition family. Therefore local stability must not be presented as a substitute for global minimization.

## 7. Engineering mapping

- `structure/theory_stability.py` implements the explicit local-stability and minimal-stability predicates.
- `structure/theory_unit_formation.py` implements the Stage 2E formation boundary.
- `materialize_unit(...)` rejects candidates that do not satisfy the supplied predicates.
- `tests/test_theory_unit_formation.py` locks the stable, unstable, non-minimal, explicit-neighborhood, and tie cases.

## 8. Remaining closure targets

### Stage 2F — Existence

State sufficient conditions under which the explicit admissible family is non-empty and the finite minimization/materialization problem has at least one solution.

### Stage 2G — Uniqueness / equivalence

Separate uniqueness of a selected representative from uniqueness modulo legal relabeling. A deterministic implementation tie-break is not a mathematical uniqueness theorem.

### Stage 3 — Relation formation

Define exactly when already-materialized Units may be connected by an explicit Relation. Relation formation must not be inferred from primitive equality or geometric proximity unless separately defined.

## Verdict

**Stage 2E is implementation-closed as an explicit predicate boundary, but not promoted to a universal Unit-existence or Unit-uniqueness theorem.**
