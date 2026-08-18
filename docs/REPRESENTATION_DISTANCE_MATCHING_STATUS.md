# Representation distance and matching: formal status

## Frozen statement

For a supplied representation `phi(W) in R^23`, the current frozen distance is

`D_R(W1,W2) = ||phi(W1) - phi(W2)||_2`.

The implementation in `structure/theory_distance.py` is therefore a direct
implementation of the stated metric, not a learned metric.

## What follows and what does not follow

The Euclidean construction gives non-negativity, symmetry, and the triangle
inequality in representation space. It does **not** establish that distinct
structural worlds have distinct representations. Thus `D_R=0` is only equality
of the supplied representations unless injectivity is separately proved.

## Matching

`select_matching` is an explicit argmin over a supplied admissible set:

`M* in argmin_{M in A} C(M)`.

The candidate set and cost function are inputs. The implementation therefore
makes no hidden claim about a unique correspondence model or a specific cost
decomposition.

A deterministic tie-break is an implementation detail only; it must not be
reported as mathematical uniqueness.

## Neural distance

No statement in this module implies

`||Z(W1)-Z(W2)||_2 = D_R(W1,W2)`.

That equality is a separate empirical/theoretical objective for Neural
Struct3D and requires its own validation.
