# Struct3D Hypothesis Elimination — Round 2

This round removes the remaining external theorem degrees of freedom from the
observation-facing path.

## 1. Model Universe Theorem

For a valid finite observation `X`, define

`M(X) = {m_point(X), m_line(X), m_plane(X)}`.

The centroid, coordinate variances, principal coordinate axis and normal axis
are finite deterministic functions of `X`. Coordinate-axis ties are resolved
lexicographically by the fixed index rule. Therefore `M(X)` is finite,
deterministic, label-free, and unchanged up to relabeling of observation
indices.

The implementation is `ObservationModelFamily.from_observation(X)` and its
frozen projection is `ObservationDerivedContext.model_family`.

## 2. Boundary-Regularization Graph Definition/Theorem

For `i<j`, define

`w_ij(X) = 1/(1 + ||x_i-x_j||/diam(X))`.

Set

`G_B(X) = (Omega_X,E_B,w)` with every unordered pair as an edge.

For `n>1`, `G_B(X)` is finite, complete, strictly positive and permutation
compatible. The normalized cut

`B_X(P) = cut_w(P) / sum_E w_e`

is therefore a deterministic observation-derived regularizer. No external
adjacency graph is needed by the theory-facing Stage 2D path.

## 3. Observation-Derived Relation Predicate Theorem

Let

`C_R(X) = {(i,j): i != j}`.

For candidate Units define

`d_X(u_i,u_j) = min_{p in u_i,q in u_j} ||x_p-x_q|| / diam(X)`

and

`c_X(u_i,u_j) = 1/(1+d_X(u_i,u_j))`.

Freeze

`Q_X(u_i,u_j) <=> u_i != u_j and c_X(u_i,u_j)>0`.

For valid finite observations, every distinct non-empty pair satisfies
`Q_X`. Hence `Q_X` is deterministic, finite, label-free and quotient
compatible. The materialized relation set is exactly the admitted subset of
`C_R(X)` with distance/confidence evidence.

This theorem does not claim that proximity is the unique universal semantic
relation law; the separate `H^2` boundary-contact relation remains an explicit
alternative geometry theorem.

## 4. Canonical observation-derived Stage 2D energy

The theory-facing energy is

`E_X(P) = sum_A min_{m in M(X)} [F_X(A,m)+k(m)] + B_X(P)`.

The complexity and boundary coefficients are frozen dimensionless constants
`1` and `1`; they are not caller-selected hyperparameters.

The separation quantity is not an input. Define

`delta_X = min { |E_X(P)-E_X(Q)| : P,Q in Gamma(X), P not~Q,
                 |E_X(P)-E_X(Q)| > 0 }`,

with `delta_X=0` when no positive gap exists.

Strict-separation theorems use the derived condition `delta_X>0` rather than
an externally supplied margin.

## 5. Unified quotient closure

Every object in the theory-facing path is now a function of the same `X`:

`X -> A_max(X)=Gamma(X) -> M(X), G_B(X), N_X,S_X,C_R(X),Q_X`

`-> E_X -> argmin -> U_X -> R_X -> W_X -> Phi_X(W_X) -> D_R`.

Thus the remaining theorem assumptions are finite-observation validity
conditions, not independently supplied candidate/model/boundary/relation/
energy hyperparameters.

The generic low-level APIs remain available for mathematical regression tests,
but they are not the provenance path used by the closed observation-facing
pipeline.
