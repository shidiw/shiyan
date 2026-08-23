# Struct3D Hypothesis Elimination — Round 2

This round removes the remaining external theorem degrees of freedom from the
observation-facing path while keeping the computational approximation explicit.

## 1. Model Universe Theorem

For a valid finite observation `X`, define

`M(X) = {m_point(X), m_line(X), m_plane(X)}`.

The centroid, coordinate variances, principal coordinate axis and normal axis
are finite deterministic functions of `X`. Coordinate-axis ties are resolved
by fixed deterministic rules. Therefore `M(X)` is finite, deterministic,
label-free, and quotient compatible.

## 2. Boundary-Regularization Graph

For `i<j`, define

`w_ij(X) = 1/(1 + ||x_i-x_j||/diam(X))`.

Set `G_B(X)` to the complete weighted graph on the observation index universe.
The normalized cut `B_X(P)` is therefore observation-derived and needs no
external adjacency graph.

## 3. Candidate Universe and Computational Family

`A_max(X) = Pi(Omega_X)` is the complete finite mathematical admissible family.
It is the theorem-level universe and is not enumerated by the scalable runtime
for large observations.

The canonical computational family is

`Gamma(X) subset A_max(X)`,

with deterministic whole, singleton, and farthest-pair Voronoi partitions.
Gamma is finite, non-empty, label-free, and quotient compatible.

`A_search(X)` is now explicitly a compatibility/scalability approximation of
`Gamma(X)` and is forbidden from being the provenance source of the main
pipeline.

## 4. Stage 2E Stability Domain

`N_X(A)` is the one-point insertion/deletion neighborhood derived from `X`.
`S_X(A)` is the finite local proper-subcandidate family consisting of
one-point deletions and singleton supports.

The canonical Unit formation rule is executed as

`Stable_X(A) -> MinimalStable_X(A) -> Unit(A)`.

No externally supplied neighborhood, subcandidate family, or energy margin is
used by the observation-facing path.

## 5. Unique Relation Law

The unique frozen relation predicate is the strong observation-derived

`Q_X(A,B) <=> d_cross(A,B) <= median_pairwise_distance(A union B)`

for distinct non-empty Units.

The canonical materializer is
`theory_semantic_relation.form_observation_semantic_relations`.

The former complete-proximity predicate and the `H^2` boundary-contact law are
retained only as legacy/experimental regression APIs. They have no frozen
theoretical status and cannot create canonical World relations.

## 6. Canonical Energy

`E_X(P) = sum_A min_{m in M(X)} [F_X(A,m)+k(m)] + B_X(P)`.

Complexity and boundary coefficients are frozen at one. The separation
quantity is derived from the observation-derived Gamma family:

`delta_X = min { |E_X(P)-E_X(Q)| : P,Q in Gamma(X), P not~Q,
                 |E_X(P)-E_X(Q)| > 0 }`.

## 7. Unified Quotient Closure

For every legal observation-index permutation `pi`,

`Gamma(pi X) = pi Gamma(X)`,
`M(pi X) ~= M(X)`,
`G_B(pi X) ~= G_B(X)`,
`N_{pi X}(pi A) = pi N_X(A)`,
`S_{pi X}(pi A) = pi S_X(A)`,
`C_R(pi X) = pi C_R(X)`,
`Q_{pi X}(pi u,pi v) = Q_X(u,v)`,
`E_{pi X}(pi P) = E_X(P)`.

Hence the induced Unit, Relation, World and Representation constructions are
all quotient compatible.

## 8. End-to-End Closure

The canonical provenance chain is

`X -> A_max(X), Gamma(X) -> M(X), G_B(X), N_X, S_X`

`-> E_X -> Stage2E -> U_X -> C_R(X) -> Q_X -> R_X -> W_X -> Phi_X(W_X) -> D_R`.

The only theorem assumptions left at the pipeline boundary are validity of the
finite observation itself. `A_search`, explicit relation predicates, explicit
boundary graphs, external margins, and caller-selected model families are no
longer assumptions of the canonical observation-facing path.
