# Struct3D Observation-Derived Boundary Closure

## 1. Observation domain

Let

`X=(x_0,...,x_{n-1})`, `x_i in R^3`,

with finite `n>=1` and positive diameter under the existing `Observation3D`
contract. Let

`Omega_X={0,...,n-1}`.

The action of a permutation `pi` on X is index relabeling only; geometric
coordinates are unchanged as a set.

## 2. Candidate family theorem

Define

`A_max(X)=Pi(Omega_X)`

and freeze

`Gamma(X)=A_max(X)`.

### Proposition 2.1

`Gamma(X)` is finite, non-empty, and quotient-compatible.

### Proof

`Omega_X` is finite, hence its partition lattice is finite. The one-block
partition and the singleton partition both exist, so the family is non-empty.
For any permutation `pi` of `Omega_X`, applying `pi` to every block maps set
partitions bijectively to set partitions. Therefore `pi(Gamma(X))=Gamma(X)`.

## 3. Model family theorem

Define

`M(X)={m_0(X),m_1(X),m_2(X)}`

where `m_0` is the centroid point model, `m_1` is the affine coordinate line
through the centroid along the largest coordinate-variance axis, and `m_2` is
the affine coordinate plane through the centroid normal to the smallest
coordinate-variance axis. Their complexities are `0,1,2`.

### Proposition 3.1

`M(X)` is finite and determined solely by X.

### Proof

All quantities are finite sums of coordinates. The variance ordering uses the
finite lexicographic tie rule already encoded by the implementation. Hence the
three models are deterministic functions of X and no semantic label is used.

## 4. Boundary graph theorem

Define `G_B(X)` on `Omega_X` by

`w_ij = 1/(1+||x_i-x_j||/diam(X))`, for `i<j`.

### Proposition 4.1

For `n>1`, `G_B(X)` is finite, complete, and has strictly positive total edge
weight. It is invariant under observation-index relabeling up to graph
isomorphism.

### Proof

There are exactly `n(n-1)/2` edges. Since distances and the diameter are
finite and non-negative, every weight is in `(0,1]`. Relabeling only permutes
edge identities while preserving their weights.

## 5. Stability-domain theorem

For a Unit support `S subseteq Omega_X`, define `N_X(S)` by all supports obtained
from S by one insertion or one deletion, omitting the empty support. Define
`S_X(S)` as every non-empty proper subset of S.

### Proposition 5.1

Both `N_X(S)` and `S_X(S)` are finite and quotient-compatible.

### Proof

There are at most `n+|S|` one-index moves and at most `2^{|S|}-2` proper
non-empty subsets. A permutation maps insertion/deletion and subset inclusion
bijectively, so the constructions commute with relabeling.

## 6. Relation-candidate theorem

For a materialized Unit family `U_X=(u_0,...,u_{k-1})`, define

`C_R(X)={(i,j):0<=i,j<k, i!=j}`.

The notation `C_R(X)` suppresses the dependence of the candidate domain on the
X-derived materialized Unit family.

### Proposition 6.1

`C_R(X)` is finite and quotient-compatible.

### Proof

Its cardinality is `k(k-1)`. A Unit relabeling induces the corresponding
permutation of ordered pairs, so the set is preserved up to relabeling.

## 7. Observation-derived relation realization

For candidate Units `u_i,u_j`, define

`d_X(u_i,u_j)=min{||x_p-x_q|| : p in u_i, q in u_j}/diam(X)`.

Then define confidence

`c_X(u_i,u_j)=1/(1+d_X(u_i,u_j))`.

The closed relation path materializes a finite `proximity` relation for every
pair in `C_R(X)` and records `(d_X,c_X)` as evidence.

This is an observation-derived relation law. It is not claimed to replace the
separate H^2 boundary-contact theorem as the unique universal Struct3D relation
semantics.

## 8. Structural Representation Coordinate Theorem

Define `Phi_X(W)` by the fixed seven groups of the v4.0 schema:

1. model-type histogram;
2. support-composition histogram;
3. Unit-count/non-singleton/component statistics;
4. relation-type histogram;
5. relation-confidence min/mean/max;
6. Unit-occupancy min/mean/max;
7. global structural counts.

### Theorem 8.1

For every valid finite X and every X-derived finite World W, `Phi_X(W)` is a
well-defined element of `R^23` and is invariant under Unit relabeling.

### Proof

Each coordinate is a finite real statistic of finite supports, finite relation
sets, finite model scores, or finite graph topology. Therefore all coordinates
are finite. Unit relabeling only permutes the terms entering histograms,
min/max/mean statistics, and graph traversal; none of those values changes.
Thus `Phi_X` descends to the finite Unit quotient.

No injectivity statement follows: two quotient-distinct Worlds can share the
same 23 statistics.

## 9. End-to-end closure

The closed observation-derived path is therefore

`X`
`  -> A_max(X)=Gamma(X)`
`  -> M(X), G_B(X), N_X, S_X, C_R(X)`
`  -> E_X`
`  -> finite argmin / Unit formation`
`  -> observation-derived Relations`
`  -> W=(U,R,Phi)`
`  -> Phi_X(W) in R^23`
`  -> D_R.

The remaining open claims are semantic adequacy of E_X, injectivity or
information completeness of Phi_X, a unique universal relation theorem, and
Object/Instance/Hierarchy and neural latent-metric theorems.
