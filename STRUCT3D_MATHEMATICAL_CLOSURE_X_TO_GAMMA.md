# Struct3D mathematical closure: X -> A_max(X) -> Gamma(X)

## Frozen definition

Let the observation be a finite non-empty set

`X = {x_0, ..., x_{n-1}}`, `n < infinity`,

with index universe

`Omega_X = {0, ..., n-1}`.

The maximal observation-derived admissible family is the complete finite
partition lattice

`A_max(X) = Pi(Omega_X)`.

No semantic labels, primitive labels, neural networks, thresholds, or legacy
heuristics are used in this definition.

The frozen engineering candidate family is

`Gamma(X) = A_max(X)`.

A candidate partition is materialized as a finite collection of the single
frozen `StructuralUnit` type. Unit identity remains `(G, theta)`; the default
candidate materializer uses the support `G` and empty explicit attributes,
while a separate observation-derived unit transform may supply `theta`.

## Theorem: Observation-Derived Candidate Family

For finite non-empty `X`, `Gamma(X)` is finite and non-empty, and is compatible
with every relabeling permutation `pi` of the observation indices:

`Gamma(pi X) = pi Gamma(X)`.

### Proof

`Omega_X` is finite with `n` elements. Its partition lattice has cardinality
`B_n`, the nth Bell number. Therefore

`|A_max(X)| = B_n < infinity`.

Since `Gamma(X)=A_max(X)`, Gamma is finite. The one-block partition
`{Omega_X}` belongs to the partition lattice, so Gamma is non-empty.

For a permutation `pi`, mapping each block `A` to `pi(A)` maps partitions to
partitions and is bijective. Hence

`pi Pi(Omega_X) = Pi(Omega_X)`

up to the canonical index relabeling, giving

`Gamma(pi X) = pi Gamma(X)`.

Therefore Gamma is quotient-compatible. QED.

## Stage 2D closure

Given an explicit Stage 2D energy `E_2D(X,P)`, the theory-facing selection is

`P*(X) in argmin_{P in Gamma(X)} E_2D(X,P)`.

Because Gamma is finite and non-empty and Stage 2D rejects non-finite energy,
the argmin is attained. The resulting Struct3D Unit collection is the
materialization of `P*`.

This closes the upstream chain:

`X -> A_max(X) = Gamma(X) -> argmin E_2D -> StructuralUnit`.

## Scope boundary

This theorem proves legality of the candidate domain and its quotient
compatibility. It does not claim that the complete Bell partition lattice is
computationally efficient for large `n`. Practical pruning may only be
promoted later if the pruning predicate is itself defined from observation,
finite, non-empty, and quotient-compatible and is proved to be a subfamily of
`A_max(X)`.
