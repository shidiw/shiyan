# Struct3D Mathematical Closure — Stage 2D: Energy

## 0. Status

Stage 2D closes the **energy functional at a parameterized mathematical boundary**.

This is a newly derived formalization built on the preserved historical skeleton

`E = E_fit + lambda_c C + lambda_b B`.

It is **not** a claim that the historical document already contained the exact formulas below. The distinction is deliberate: the historical skeleton is preserved, while the missing domains, normalization, and concrete admissible model/graph inputs are now made explicit.

The governing chain is:

`mathematical definition -> derivation -> engineering implementation -> regression contract`.

## 1. Energy domain

Let the finite observation be

`X = {x_1, ..., x_n},  x_i in R^3`.

Let `P = {A_1, ..., A_K}` be an admissible finite partition of the observation index set.

The energy is a **partition functional**:

`E_X(P) >= 0`.

A unit-level contribution is defined first and then summed over partition cells.

This resolves the previous ambiguity between an energy on a region and an energy on a complete partition: the canonical object for selection is `E_X(P)`, while each cell has a derived local contribution `e_X(A)`.

## 2. Geometric scale normalization

Define the observation scale by its diameter

` s(X) = diam(X) = max_{i,j} ||x_i - x_j||_2 `.

The theory domain excludes `s(X)=0`, because a zero-diameter observation has no non-trivial geometric scale.

All squared geometric residuals are divided by `s(X)^2` and averaged by the number of points in the cell. Therefore the fit term is dimensionless and is not changed merely by duplicating points or applying a global coordinate scaling.

## 3. Explicit geometric model family

Let `M` be a finite, explicitly supplied family of geometric models. Each model `m in M` has:

- a residual `rho_m(x) >= 0`, interpreted as squared distance from `x` to the model;
- a non-negative complexity `kappa(m) >= 0`.

No plane/sphere/cylinder classifier is built into the theory. Such models may be supplied as one particular model family, but their presence is an engineering choice unless a future theorem freezes that family.

For a non-empty candidate cell `A`, define

`F_X(A,m) = (1 / (|A| s(X)^2)) sum_{i in A} rho_m(x_i)`.

The unit cost is

`e_X(A) = min_{m in M} [ F_X(A,m) + lambda_c kappa(m) ]`.

This makes model fitting and complexity a single variational choice rather than two independently selected labels.

## 4. Boundary functional

Let `G_X=(V_X,E_X,w)` be an explicitly supplied weighted observation graph with `V_X={1,...,n}`, non-negative edge weights, and positive total edge weight

`W_G = sum_{(i,j) in E_X} w_ij > 0`.

For a partition `P`, define the normalized cut boundary energy

`B_X(P) = (1/W_G) sum_{(i,j) in E_X} w_ij 1[c_P(i) != c_P(j)]`.

Thus

`0 <= B_X(P) <= 1`.

The graph is an explicit mathematical input. The theory does not silently infer adjacency from a radius threshold, primitive equality, or connected-component heuristic.

The boundary term is therefore spatially grounded without introducing a new historical `E_spatial` term. This preserves the three-term historical skeleton rather than replacing it with a four-term objective.

## 5. Frozen Stage 2D energy

For an admissible partition `P={A_1,...,A_K}`, define

`E_X(P) = sum_{r=1}^K e_X(A_r) + lambda_b B_X(P)`.

Equivalently,

`E_X(P) = sum_r min_{m in M} [F_X(A_r,m) + lambda_c kappa(m)] + lambda_b B_X(P)`.

The required parameter restrictions are

`lambda_c >= 0,  lambda_b >= 0`.

No universal numerical values for these coefficients are asserted by the theorem. They are declared model parameters and must be fixed by the experimental protocol when the model is instantiated.

## 6. Immediate mathematical properties

### Non-negativity

Every term is non-negative, hence

`E_X(P) >= 0`.

### Finiteness

For finite `X`, a finite model family with finite residuals and finite complexities, and a finite weighted graph, `E_X(P)` is finite for every admissible partition.

### Scale invariance of the fit term

Under a global scaling `x_i' = a x_i` with `a != 0`, both squared residuals and `s(X)^2` scale by `a^2`. Therefore `F_X(A,m)` is unchanged, provided the model residual transforms consistently with the same geometry.

### Duplication invariance of the fit average

Replicating every point the same number of times leaves the mean residual of each cell unchanged. Thus the geometric fit does not depend on raw point count alone.

### Boundary normalization

`B_X(P)` is invariant to a common positive rescaling of all graph weights.

## 7. What this closes

Stage 2D now closes the following previously missing objects:

1. exact energy domain: partition;
2. exact fit domain: finite model family over 3-D observations;
3. fit normalization: cell mean divided by observation diameter squared;
4. complexity: explicit non-negative model functional `kappa`;
5. boundary: normalized weighted graph cut;
6. coefficient constraints: non-negative `lambda_c, lambda_b`;
7. finiteness and non-negativity conditions;
8. implementation boundary and regression tests.

## 8. What remains open

This stage does **not** prove that this parameterized energy is the unique historical Struct3D energy. It also does not prove:

- a unique universal model family `M`;
- a unique universal complexity functional `kappa`;
- a unique observation graph construction;
- a universal value of `lambda_c` or `lambda_b`;
- that every global minimizer is unique;
- that every locally stable candidate is a Structural Unit;
- that pairwise merge delta is the universal emergence law.

Those are separate mathematical or empirical questions.

## 9. Variational consequence for Stage 2C

Let `A(X)` be a finite non-empty admissible partition family and let

`P* in argmin_{P in A(X)} E_X(P)`.

For any explicitly supplied neighborhood `N(P*) subseteq A(X)`, every `Q in N(P*)` satisfies

`E_X(P*) <= E_X(Q)`.

Therefore the global minimizer is locally stable with respect to every declared admissible neighborhood.

This is a direct consequence of the argmin definition. The converse is not claimed: a local minimum need not be a global minimum.

For a declared split neighborhood `Split(P,A)`, the corresponding split-stability condition is simply

`E_X(P) <= E_X(P^{A -> A_1,A_2})`

for every explicitly admissible split. This is a theorem about the declared neighborhood, not a universal merge law.

## 10. Engineering realization

Implemented in:

`structure/theory_energy_model.py`

with:

- `Observation3D`;
- `GeometricModel`;
- `WeightedObservationGraph`;
- `Stage2DEnergy`.

Regression contracts are in:

`tests/test_theory_energy_model.py`.

The existing `structure/theory_energy.py` remains intact as the generic externally supplied functional interface. The legacy `structure/energy.py` remains regression-only and is not imported by the new Stage 2D model.

## 11. Release verdict

**Stage 2D is closed at the parameterized mathematical-functional level.**

The upstream chain is now:

`X -> explicit admissible A(X) -> E_X(P) -> argmin -> explicit stability neighborhood -> Stable -> MinimalStable -> materialized StructuralUnit`.

The remaining central theorem gap is no longer the definition of energy itself; it is the relation between the chosen admissible family, stability/minimality, and Structural Unit emergence.
