# Struct3D Final Observation-Derived Boundary Closure

The canonical theory-facing runtime has one observation provenance carrier
`ObservationDerivedContext.from_points(X)`.

The six formerly external boundaries are now frozen as follows:

- `A_max(X)`: complete finite partition lattice of the observation index universe.
- `Gamma(X)`: unique deterministic computational subfamily with no strategy argument.
- `M(X)`: fixed observation-derived point/line/plane model family.
- `G_B(X)`: complete observation-index boundary graph with deterministic distance weights.
- `N_X(u)` / `S_X(u)`: deterministic insertion/deletion and proper-subcandidate families.
- `C_R(X)`: all ordered distinct pairs of the selected observation-derived Unit family.
- `Phi_X`: unique 23-D observation-derived coordinate map that requires the same
  `ObservationDerivedContext` attached to the World.

Stage 2D consumes `M(X)` and `G_B(X)` from the same context. Stage 2E consumes
`N_X`, `S_X`, and the X-derived Unit competitor family. Stage 3 consumes the
actual `C_R(X)` domain and evaluates only the unique `Q_X` predicate. World is
constructed from those Units and Relations, and `Phi_X` rejects a World carrying
a different observation context.

Legacy explicit-input constructors remain available only as compatibility APIs;
they are not canonical theorem provenance.
