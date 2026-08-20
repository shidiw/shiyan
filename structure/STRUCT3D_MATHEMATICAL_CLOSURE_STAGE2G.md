# Struct3D Mathematical Closure — Stage 2G

## Scope

Stage 2G separates **uniqueness of a selected admissible minimizer** from deterministic implementation tie-breaking and from structural equivalence.

## 1. Uniqueness theorem

Let `A(X)` be a finite admissible family and let `E` be finite on it. Suppose `P* in A(X)` satisfies

`E(P*) < E(P)`

for every distinct `P in A(X)`.

### Theorem 2G.1 — Strict minimizer uniqueness

Under the strict inequality above,

`argmin_{P in A(X)} E(P) = {P*}`.

### Proof

The strict inequality states that every distinct admissible competitor has energy strictly greater than `E(P*)`. Hence no distinct competitor can attain the minimum. Since `P*` attains the minimum, the argmin set contains exactly `P*`. QED.

## 2. Engineering realization

`structure/theory_uniqueness.py::is_unique_minimizer` checks the strict inequality against the explicitly supplied competitor family.

`prove_unique_minimizer(...)` returns a uniqueness witness only when that strict condition holds. Equal-energy ties are rejected rather than resolved by Python ordering.

## 3. What is not claimed

Stage 2G does not claim:

- uniqueness merely because the implementation returns the first tied candidate;
- uniqueness of Structural Units when the global partition minimizer is tied;
- structural equivalence from equal energy;
- structural equivalence from `D_R = 0`;
- uniqueness modulo relabeling without an explicit equivalence relation and proof.

The latter issue belongs to the already defined canonical/equivalence machinery and must not be silently substituted for energy uniqueness.

## 4. Closed global-selection chain

Under the Stage 2F hypotheses:

`A(X) non-empty + finite + E finite`

implies

`argmin E != emptyset`.

Adding the Stage 2G strict-separation hypothesis gives

`argmin E = {P*}`.

Thus the global selection chain is conditionally closed up to unique minimization.

## Verdict

**Stage 2G is conditionally mathematically closed:** strict separation of one admissible candidate from all distinct competitors proves unique global minimization. No tie-breaking heuristic is promoted to a theorem.
