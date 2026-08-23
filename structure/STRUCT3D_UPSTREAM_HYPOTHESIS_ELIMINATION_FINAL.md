# Struct3D Upstream Hypothesis Elimination — Final Runtime Closure

## Canonical provenance

The canonical observation-facing execution is now

`X -> A_max(X), Gamma(X), M(X), G_B(X), N_X, S_X`

`-> E_X -> Stable_X -> MinimalStable_X -> Unit_X`

`-> C_R(X) -> Q_X -> R_X -> W_X -> Phi_X(W_X)`.

`A_search(X)` is not a theorem boundary and is not called by the canonical
pipeline. It is retained only as a scalability-approximation compatibility API.

## 1. A_max versus Gamma

`A_max(X)=Pi(Omega_X)` is the complete finite mathematical admissible universe.
For large observations it is not enumerated. The runtime uses the frozen finite
computational family `Gamma(X) subset A_max(X)`.

The current Gamma registry is deterministic and observation-only:

1. whole-observation partition;
2. singleton partition;
3. deterministic farthest-pair Voronoi bipartition.

Every Gamma candidate is validated as a partition of the same observation
universe. `A_search` is merely a compatibility alias and is explicitly excluded
from canonical provenance.

## 2. Stage 2E is now an executed pipeline stage

For every Unit appearing in Gamma, the canonical pipeline evaluates

`Stable_X(u)`, then `MinimalStable_X(u)`, and only surviving Units enter the
materializable Unit family.

The observation-derived `N_X` and `S_X` are finite local constructions. The
Stage 2D unit energy is used directly; no external Stage 2E energy or margin is
supplied.

A Gamma partition is admissible to the final Stage 2D argmin only if every Unit
in that partition survives the Stage 2E chain.

## 3. Unique Q_X

The unique frozen relation law is the strong observation-derived predicate

`Q_X(A,B) <=> d_cross(A,B) <= median_pairwise_distance(A union B)`.

The canonical materializer is
`theory_semantic_relation.form_observation_semantic_relations`.

The former weak complete-proximity law and H^2 boundary-contact law remain only
for regression/experimental compatibility. They have no co-equal theory status
and are forbidden from creating canonical World relations.

## 4. One Unit → Relation → World lineage

The selected Stage 2E-admissible Gamma partition defines the final Unit family
`U_X`.

`C_R(X)` is generated directly from that selected Unit family as every ordered
pair of distinct Units.

The same Units and the same `ObservationDerivedContext` are passed to `Q_X`,
relation materialization, World construction and `Phi_X`. Consequently no
external relation family or representation context can be injected between
Unit and World.

## 5. What this closes

The canonical runtime no longer has these external upstream assumptions:

- candidate family;
- model family;
- boundary graph;
- stability neighborhood;
- proper-subcandidate family;
- relation candidate domain;
- relation predicate;
- World/Representation provenance.

The remaining open claims are semantic/theoretical research claims such as
energy semantic adequacy, representation injectivity, universal object/hierarchy
emergence, and neural metric preservation. They are not hidden runtime
assumptions.
