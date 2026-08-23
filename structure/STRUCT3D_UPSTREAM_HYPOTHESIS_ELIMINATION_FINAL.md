# Struct3D Upstream Hypothesis Elimination — Final Runtime Closure

## Canonical provenance

The canonical observation-facing execution is now

`X -> A_max(X), Gamma(X), M(X), G_B(X), N_X, S_X`

`-> E_X -> Stable_X -> MinimalStable_X -> Unit_X`

`-> C_R(X) -> Q_X -> R_X -> W_X -> Phi_X(W_X)`.

The important final change is that these are no longer merely context-backed
interfaces with caller-selectable construction parameters. Each canonical
boundary is a deterministic function of the same finite observation `X`.

`A_search(X)` is not a theorem boundary and is not called by the canonical
pipeline. It is retained only as a scalability-approximation compatibility API.

## 1. A_max and the unique Gamma

`A_max(X)=Pi(Omega_X)` is the complete finite mathematical admissible universe.
For large observations it is not enumerated. The runtime uses the frozen finite
computational family `Gamma(X) subset A_max(X)`.

The canonical `Gamma_X(X)` has **no external strategy argument**. It is uniquely
determined from `X` by three deterministic constructions:

1. whole-observation partition;
2. singleton partition;
3. deterministic farthest-pair Voronoi bipartition.

Every Gamma candidate is validated as a partition of the same observation
universe. Historical strategy selection survives only behind `A_search`, which
is explicitly outside canonical provenance.

## 2. Unique M(X) and G_B(X)

`M(X)` is the fixed observation-derived model universe `{point,line,plane}`.
Model geometry and deterministic signatures are reconstructed from `X`; no
caller-supplied model family enters Stage 2D.

`G_B(X)` is the complete finite observation-index boundary graph with weight
`w_ij = 1/(1+d(x_i,x_j)/s(X))`. Stage 2D consumes exactly this graph and its
observation-derived weights.

## 3. Unique N_X and S_X

`N_X(u)` is the deterministic one-point insertion/deletion neighborhood of a
Unit support inside `Omega_X`. `S_X(u)` is the deterministic proper
subcandidate family consisting of one-point deletions and singleton supports.
No external neighborhood or competitor family is accepted by the canonical
Stage 2E path.

## 4. Unique C_R(X) and Q_X

For the selected observation-derived Unit family `U_X`,

`C_R(X) = {(i,j): i != j, u_i,u_j in U_X}`.

The canonical Stage 3 materializer consumes this exact candidate domain rather
than reconstructing another pair universe locally.

The unique frozen relation law is

`Q_X(A,B) <=> d_cross(A,B) <= median_pairwise_distance(A union B)`.

The former weak complete-proximity law and H^2 boundary-contact law remain only
for regression/experimental compatibility. They have no co-equal theory status
and are forbidden from creating canonical World relations.

## 5. Unique Phi_X

`Phi_X` is the fixed 23-dimensional deterministic coordinate map constructed
from `X` and the `X`-derived World. The canonical map now rejects a World whose
attached observation context is not the exact context used to construct
`Phi_X`. This prevents an external observation/representation context from
being injected between World and Representation.

## 6. One Unit -> Relation -> World lineage

The selected Stage 2E-admissible Gamma partition defines the final Unit family
`U_X`.

The same `U_X` and the same `ObservationDerivedContext` are passed to `C_R(X)`,
`Q_X`, relation materialization, World construction and `Phi_X`. Consequently
there is one provenance lineage and no independent caller-supplied candidate,
model, graph, neighborhood, relation-domain, or representation map in the
canonical execution.

## 7. What this closes

The canonical runtime has eliminated the following upstream external
assumptions:

- candidate family `A(X)` / `Gamma(X)`;
- model family `M(X)`;
- boundary graph `G_B(X)`;
- stability neighborhood `N_X` and proper-subcandidate family `S_X`;
- relation candidate domain `C_R(X)`;
- representation provenance `Phi_X`.

The remaining open claims are semantic/theoretical research claims such as
energy semantic adequacy, representation injectivity, universal object/
hierarchy emergence, and neural metric preservation. They are not hidden
runtime assumptions.
