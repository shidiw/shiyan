# Struct3D Mathematical Closure — Stage 2F

## Scope

Stage 2F closes the **conditional existence** part of the global formation problem without inventing the missing raw-observation candidate generator.

The preserved theory leaves the construction

`X -> A(X)`

as an unresolved boundary. Therefore Stage 2F does not claim that `A(X)` is non-empty for every observation. Instead it proves the exact finite-set result that is justified once an explicit admissible family is supplied.

## 1. Hypotheses

Let `X` be a finite indexed observation universe and let

`A(X) = {P_1, ..., P_m}`

be an explicitly supplied admissible family of valid partitions, with

`m >= 1`.

Let

`E : A(X) -> R`

be a scalar energy functional such that

`E(P_i) in R`

for every candidate.

No formula for `E` is invented here.

## 2. Existence theorem

### Theorem 2F.1 — Finite admissible minimizer existence

If `A(X)` is finite and non-empty and `E` is finite on `A(X)`, then

`argmin_{P in A(X)} E(P) != emptyset`.

### Proof

The image

`E(A(X)) = {E(P_1), ..., E(P_m)}`

is a finite non-empty subset of `R`. Every finite non-empty subset of `R` has a minimum. Hence there exists some `P* in A(X)` such that

`E(P*) = min_{P in A(X)} E(P)`.

Therefore

`P* in argmin_{P in A(X)} E(P)`,

so the argmin set is non-empty. QED.

## 3. Engineering realization

`structure/theory_existence.py::prove_finite_minimizer_exists` enforces exactly these hypotheses:

1. the supplied candidate family is non-empty;
2. every candidate is a valid finite `Partition`;
3. every supplied energy value is finite.

It returns one minimizing witness and its energy.

A deterministic implementation choice on ties is not interpreted as uniqueness.

## 4. Unit consequence

Every valid partition returned by the theorem contains at least one non-empty Structural Unit because `Partition` enforces non-empty complete coverage.

Therefore the theorem establishes:

`P* exists => U(P*) is non-empty`.

This is a consequence of the frozen Partition definition, not a theorem that a particular raw observation necessarily generates a candidate family.

## 5. What remains unproved

Stage 2F does **not** prove:

1. `A(X) != emptyset` for every raw observation `X`;
2. that a particular geometric algorithm constructs the correct `A(X)`;
3. uniqueness of `P*`;
4. uniqueness of the resulting Units;
5. that `P*` is locally stable under the Stage 2E neighborhood;
6. that a Stage 2E `Materializable` candidate exists for every observation;
7. observation invariance of the selected Unit.

The materializable-witness helper is therefore an explicit witness test rather than an existence theorem.

## 6. Closed chain after Stage 2F

The theory-safe global chain is now

`X -> explicit non-empty finite A(X) -> finite E -> P* in argmin E -> Units(P*)`.

The local formation chain remains separate:

`candidate u -> explicit N(u), S(u) -> Stable -> MinimalStable -> Materializable(u)`.

The two chains must not be conflated.

## Verdict

**Stage 2F is conditionally mathematically closed:** finite, non-empty admissible families with finite supplied energy have an attained global minimizer. The universal observation-to-admissible-family existence problem remains open and is not hidden by implementation heuristics.
