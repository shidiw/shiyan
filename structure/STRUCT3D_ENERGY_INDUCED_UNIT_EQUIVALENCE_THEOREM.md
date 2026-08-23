# Energy-Induced Structural Unit Equivalence — Complete Unit Invariant Closure

## 1. Audit verdict

The previous Unit-level key was not a complete quotient invariant for the
observation-facing theory. A key based directly on `unit.indices` preserves
arbitrary observation labels. Two relabeled copies of the same observed
support can therefore receive different keys.

The missing object is now frozen as the observation-aware canonical invariant

`Can_U^X(u) = ( sort({x_i : i in G_u}), Freeze(theta_u) )`.

The historical `primitive` field is excluded because the frozen mathematical
Unit is `u=(G,theta)`; primitive is compatibility metadata.

Implementation: `structure/theory_unit_invariant.py`.
Regression contract: `tests/test_theory_unit_invariant.py`.

## 2. Unit quotient

Let the finite observation be

`X=(x_0,...,x_{n-1})`.

Let a Unit be

`u=(G,theta)`, with `empty != G subseteq {0,...,n-1}`.

Two Units are equivalent under the observation-label quotient, written
`u ~_X v`, when a permutation of the finite observation indices transports one
support to the other while preserving the observed point values and the frozen
attribute object `theta`.

This quotient removes only arbitrary index names. It does not identify units
with different observed geometry or different `theta`.

## 3. Definition of Can_U

For every valid finite Unit `u=(G,theta)`, define

`Can_U^X(u) = ( sort((x_i)_{i in G}), Freeze(theta) )`.

`sort` is lexicographic sorting of the finite point tuple and `Freeze` is the
deterministic recursive finite representation already used by the theory
boundary.

Thus `Can_U^X(u)` is finite, deterministic and hashable.

## 4. Invariance theorem

### Theorem 4.1 — Can_U quotient invariance

For every finite observation `X`, Unit `u`, and admissible observation-index
permutation `pi`,

`Can_U^X(u) = Can_U^{pi X}(pi u)`.

### Proof

The permutation only changes the names attached to the same finite observed
points. Transporting the Unit support by the inverse permutation therefore
selects exactly the same multiset of physical observations. Lexicographic
sorting removes their order, and `theta` is unchanged by the label action.
Hence both components of `Can_U` are identical. QED.

## 5. Completeness theorem

### Theorem 5.1 — Can_U is a complete invariant

For finite valid Units `u,v` over finite observations in the same observation
quotient class,

`Can_U^X(u) = Can_U^X(v)`

if and only if

`u ~_X v`.

### Proof

**(=>)** Equality of `Can_U` gives equality of the sorted finite point
multisets and equality of `Freeze(theta)`. Therefore the supports have equal
cardinality and can be bijected point-for-point while preserving the observed
point values; the finite index bijection extends to a permutation of the full
observation index set. Since `theta` is equal, the permutation transports `u`
to `v`. Hence `u ~_X v`.

**(<=)** If `u ~_X v`, the quotient action preserves the observed point
multiset and `theta`. By Theorem 4.1 both Units have the same `Can_U`. QED.

Therefore

`Can_U^X(u)=Can_U^X(v) <=> u~_Xv`.

This is the required injectivity on the Unit quotient.

## 6. Compatibility with Energy

The Stage 2D Unit energy may distinguish quotient classes only through
observation geometry and frozen attributes. The quotient-safe comparison is
therefore

`E_U,X(u) = E_U,X(v)` whenever `u ~_X v`.

The canonical Unit quotient key used by future energy comparisons must be
`Can_U^X`, not the raw index tuple.

A raw-index equality test remains valid only as an engineering identity test,
not as a semantic quotient test.

## 7. Compatibility with World

The Unit lineage is now

`X -> A_max(X) -> Gamma(X) -> E_X -> Stable/MinimalStable -> u -> Can_U^X(u)`.

World formation may reorder Unit positions, but the Unit identity carried into
the quotient is represented by `Can_U^X`. Therefore Unit relabeling cannot
change the underlying quotient class.

The existing World canonical form remains the finite exact canonicalization of
`W=(U,R,Phi)`; this theorem supplies the missing complete invariant at the
Unit level beneath that World quotient.

## 8. Important boundary

This theorem does **not** claim that the 23-dimensional `Phi_X` is injective.
`Can_U` is complete for the Unit quotient because it retains the full observed
support multiset and `theta`. `Phi_X` intentionally compresses World structure
into 23 coordinates and therefore requires a separate information-completeness
or injectivity theorem.

## 9. Release status

**Unit quotient closure: CLOSED.**

The previous raw-index Unit key is demoted to compatibility identity. The
observation-aware `Can_U` is the frozen complete invariant for finite
observation-derived Structural Units.
