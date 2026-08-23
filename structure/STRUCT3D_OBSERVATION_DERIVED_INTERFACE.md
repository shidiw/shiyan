# Struct3D Observation-Derived Theory Interface

## Frozen release boundary

The theorem-facing Struct3D construction is now exposed through one formal
interface:

`ObservationDerivedTheoryInterface`

with concrete implementation:

`ObservationDerivedBoundaries.from_points(X)`.

The constructor accepts **only the observation**. The former external
boundaries are projections of that one provenance carrier and are not
independent theorem inputs.

## Frozen dependency graph

```text
X
│
├── A_max(X) = Π(Ω_X)
├── Γ(X) ⊆ A_max(X)
├── M(X)
├── G_B(X)
├── N_X / S_X
│
└── E_X
      │
      └── Stable → MinimalStable → Unit
                           │
                           ├── C_R(X)
                           │      │
                           │      └── Q_X → R
                           │                 │
                           │                 └── G
                           │                     │
                           │                     └── W=(U,R,Φ)
                           │
                           └── Φ_X(W) ∈ R^23
```

## Interface members

| Former boundary | Frozen interface member | Provenance |
|---|---|---|
| `A(X)` | `A_max`, `Gamma` | finite observation index universe `Ω_X` |
| `M(X)` | `M` | deterministic model family built from `X` |
| `G_B(X)` | `G_B` | complete weighted observation graph |
| `N_X / S_X` | `N_X(unit)`, `S_X(unit)` | finite support perturbations derived from `X` |
| `C_R(X)` | `C_R` | ordered pairs of X-derived selected Units |
| `Φ_X` | `Phi_X(world)` | deterministic 23-D coordinate map from `X` and `W` |

The Stage 2D energy is exposed as `energy` and is bound to the same observation
context. `world()` and `representation()` likewise consume that same context.

## Anti-injection rule

No constructor field exists for `A_max`, `Gamma`, `M`, `G_B`, `N_X`, `S_X`,
`C_R`, or `Phi_X`. Supplying one of these as an independent argument is a
contract violation. This is enforced by the regression suite.

Low-level explicit-input APIs remain available for generic mathematical and
legacy regression use. They are compatibility APIs, not the release theorem
path.

## Mathematical status

This interface freezes **provenance and construction**, not semantic truth.
In particular:

- `A_max(X)` is a finite mathematical family;
- `Gamma(X)` is the selected observation-derived computational family;
- `M(X)`, `G_B(X)`, `N_X`, `S_X`, and `C_R(X)` are deterministic derived objects;
- `E_X` is the frozen Stage 2D derived energy extension;
- `Phi_X` is a well-defined finite coordinate map;
- no injectivity, semantic completeness, or universal relation law is claimed
  merely because the interface is frozen.

The formal interface therefore closes the **upstream hypothesis boundary**
without silently converting engineering definitions into historical theorems.
