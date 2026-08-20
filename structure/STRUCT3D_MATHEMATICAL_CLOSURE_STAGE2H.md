# Struct3D Mathematical Closure — Stage 2H: X → A(X) → Unit

## 1. Purpose

The remaining upstream gap was the missing mathematical construction from a
finite observation domain `X` to an admissible candidate family and then to a
materializable Structural Unit.

Stage 2H closes this boundary without introducing a geometric threshold,
primitive classifier, connectivity heuristic, or learned rule.

The closure is variational: admissibility is determined only by finite support
membership, while the structural energy determines which support can emerge.

## 2. Observation domain

Let

`X = {x_1, ..., x_n}`

be a finite non-empty indexed observation domain, with `n >= 1`.

In the engineering core, `X` is represented by a sorted tuple of unique
non-negative observation indices.

The finite-domain assumption is explicit. It matches the current finite
observation model used by the theory-facing partition and Unit objects.

## 3. Canonical admissible candidate family

Define

`A(X) = { u_S : empty != S subseteq X }`

where

`u_S = (S, theta_S)`

and the emergence core uses the neutral attribute assignment

`theta_S = empty map`.

This does not assert that geometry-derived attributes do not exist. It says
that attributes are not required to decide support admissibility. They may be
attached by a downstream extractor after support emergence.

Because `X` is finite,

`|A(X)| = 2^n - 1`.

Therefore `A(X)` is finite and non-empty for every finite non-empty `X`.

This is the missing unconditional existence fact for the candidate domain.

## 4. Canonical stability neighborhood

For every `u_S in A(X)`, define

`N_X(u_S) = A(X) \ {u_S}`.

Thus a candidate is tested against every competing non-identical candidate.

For `|A(X)| = 1`, the executable implementation uses the candidate itself as
a neutral equality witness because the historical `StabilityNeighborhood`
container requires a non-empty tuple. This is an engineering representation
of vacuous stability, not an additional mathematical competitor.

## 5. Stability becomes global minimality

With a finite real-valued energy

`E : A(X) -> R`,

Stage 2E stability becomes

`Stable_X(u) <=> E(u) <= E(v) for every v in A(X) \ {u}`.

Therefore

`Stable_X(u) <=> u in argmin_{v in A(X)} E(v)`.

### Proposition 5.1

For finite non-empty `A(X)` and finite-valued `E`, `Stable_X` candidates exist.

### Proof

A finite non-empty subset of `R` has a minimum. Therefore the finite set
`{E(u): u in A(X)}` has a minimum value `m`. Every candidate with energy `m`
is stable under `N_X`. Hence at least one stable candidate exists. QED.

## 6. Minimal-stable emergence

Stage 2E already defines

`MinimalStable(u) <=> Stable(u) and no proper subcandidate of u is stable`.

Under the canonical candidate family, define the proper-subcandidate family as

`S_X(u_S) = {u_T in A(X): T proper subset S}`.

Then

`EmergentUnit_X = {u_S in Stable_X : no T proper subset S is Stable_X}`.

Equivalently, `EmergentUnit_X` is the set of inclusion-minimal elements of the
stable-candidate set.

### Theorem 6.1 — Unit-emergence existence

For every finite non-empty `X` and every finite real-valued energy `E` on
`A(X)`,

`EmergentUnit_X != emptyset`.

### Proof

By Proposition 5.1, `Stable_X` is non-empty. Because `Stable_X` is finite,
choose a stable candidate with minimal support cardinality. If it had a proper
stable subcandidate, that subcandidate would have strictly smaller support,
contradicting the choice. Hence the selected candidate belongs to
`EmergentUnit_X`. QED.

## 7. What is and is not unique

The theorem proves existence, not uniqueness.

If several inclusion-minimal stable candidates have equal energy and are
incomparable under support inclusion, then

`|EmergentUnit_X| > 1`.

A deterministic implementation may select one canonical representative, but
that selection is not a uniqueness theorem.

If there is a unique strict energy minimizer `u*`, then

`E(u*) < E(u)` for every `u != u*`

and therefore

`EmergentUnit_X = {u*}`.

This is exactly the conditional uniqueness principle already established by
Stage 2G.

## 8. Materialization theorem

For every

`u in EmergentUnit_X`,

Stage 2E gives

`Stable(u) and MinimalStable(u)`.

Therefore

`Materializable(u)`.

The materialization map is simply

`M(u) = StructuralUnit(S, theta_S)`.

No support indices, attributes, or primitive labels are silently changed during
materialization.

## 9. Closed upstream chain

The upstream theory is now

`finite observation X`

`↓`

`A(X) = all non-empty supports S subseteq X`

`↓`

`finite real energy E`

`↓`

`Stable_X = argmin_{u in A(X)} E(u)`

`↓`

`inclusion-minimal stable candidates`

`↓`

`Materializable StructuralUnit u=(G,theta)`.

Thus the previous open boundary

`X -> A(X) -> Unit`

is closed at the level of existence.

## 10. Important limitation

This closure is deliberately a **support-admissibility theorem**, not a claim
that every geometrically meaningful object must be represented by an arbitrary
subset of points.

The theory now separates two questions:

1. **Existence:** every finite non-empty observation domain has a finite,
   non-empty canonical candidate family and therefore at least one emergent
   Unit.
2. **Semantic adequacy:** whether the frozen energy `E` makes the resulting
   supports correspond to the intended geometric structures.

The second question requires the energy model and its invariance properties to
be proved separately. It must not be smuggled into `A(X)` through heuristic
thresholds.

## 11. Consequence for later stages

The global partition problem can now use the same canonical principle:

`Part(X) = {finite partitions of X into non-empty canonical Units}`.

Stage 2F then supplies the conditional argmin theorem over any explicit finite
partition family, while Stage 2H supplies the canonical finite candidate domain
from the raw finite observation set.

The distinction is essential:

`A(X)` is the candidate-support family;
`Part(X)` is the partition family.

They are not interchangeable.

## Verdict

**Stage 2H closes `X → A(X) → Unit` for finite observations at the level of
existence and materialization. Uniqueness remains conditional on strict energy
separation, and semantic/geometric adequacy remains a property of the energy
model rather than of admissibility.**
