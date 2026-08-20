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
- Stage 2F is implemented by `structure/theory_existence.py` as a conditional finite-family existence theorem.
- Stage 2G is implemented by `structure/theory_uniqueness.py` as a conditional strict-minimum uniqueness theorem.

## 8. Current closure status

Stage 2F closes the conditional global-existence statement:

`A(X)` finite and non-empty + finite `E` => `argmin E` is non-empty.

Stage 2G closes the conditional uniqueness statement:

`E(P*) < E(P)` for every distinct admissible `P` => `argmin E = {P*}`.

Neither theorem claims that the raw observation-to-candidate operator `X -> A(X)` is universally non-empty. Neither theorem promotes a deterministic tie-break to mathematical uniqueness.

## Verdict

**Stages 2E–2G are now closed at the strongest level justified by the preserved theory: explicit local formation, conditional global existence, and conditional global uniqueness. The universal construction of `A(X)` and observation-invariant Unit emergence remain the genuine unresolved theory problems.**
