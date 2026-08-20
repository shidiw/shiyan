# Struct3D Mathematical Closure — Stage 2C: Stability and Minimality

## 0. Status

Stage 2C converts the previously unimplemented **stability/minimality boundary** into an explicit theory-facing interface and regression contract.

This is a closure of the **interface**, not a claim that the preserved historical documents already contain a unique stability theorem. The authoritative material requires stability against allowed structural perturbations and discusses the cost of splitting, but it does not freeze the perturbation family itself.

Therefore this stage introduces no universal threshold, no `exp(-E)` score, and no mandatory pairwise merge formula.

## 1. Frozen executable predicate

For a candidate `A`, an explicitly supplied neighborhood `N(A)`, and a finite scalar energy `E`, define:

`Stable(A; N, E) <=> E(A) <= E(B) for every B in N(A)`.

The neighborhood is an explicit input. The implementation does not infer it from geometry, connectivity, primitive labels, point counts, or legacy thresholds.

This is the precise local-minimum predicate that the current theory can safely expose without inventing the missing perturbation model.

## 2. Minimality boundary

Stability alone does not exclude a smaller stable substructure. Stage 2C therefore exposes:

`MinimalStable(A) <=> Stable(A) and no explicitly supplied proper subcandidate is Stable`.

Both the proper-subcandidate family and the neighborhood rule are explicit inputs.

The implementation deliberately does not infer `proper`, connectivity, splitting, or containment from raw observations.

## 3. Engineering realization

`structure/theory_stability.py` now provides:

- `StabilityNeighborhood` — explicit perturbation alternatives;
- `is_locally_stable(...)` — local energy-minimum predicate;
- `is_minimal_stable(...)` — stability plus absence of a supplied stable proper subcandidate.

The energy must be finite. Empty neighborhoods are rejected because a stability test without any declared alternative would be vacuous and would conceal the missing perturbation definition.

## 4. Regression contract

`tests/test_theory_stability.py` verifies:

1. equal-energy alternatives do not violate stability;
2. a lower-energy alternative violates stability;
3. empty neighborhoods are rejected;
4. non-finite energies are rejected;
5. a stable proper subcandidate prevents minimality;
6. absence of a stable proper subcandidate permits minimality under the supplied rule;
7. the neighborhood remains an explicit input rather than an inferred heuristic.

## 5. What remains mathematically open

Stage 2C does **not** prove any of the following:

- a unique geometric neighborhood `N(A)`;
- that `N(A)` must consist of pairwise merges;
- that `Delta E_merge < 0` is the universal merge law;
- that `Delta E_merge >= 0` alone is sufficient for a Structural Unit;
- that every stable/minimal candidate exists for an arbitrary point-cloud observation;
- that every stable/minimal candidate is unique;
- that the abstract candidate is automatically primitive.

Those require the missing admissibility/energy/perturbation theory to be frozen first.

## 6. Current upstream chain after Stage 2C

The implementation exposes the following chain:

`X`

`-> explicit admissible family A(X)`

`-> explicit energy E_X(P)`

`-> explicit perturbation neighborhood N(A)`

`-> Stable(A)`

`-> explicit proper-subcandidate family`

`-> MinimalStable(A)`

`-> [future Unit-emergence theorem]`

`-> StructuralUnit`

Stage 2D has now supplied a parameterized, normalized energy functional while keeping the model family and observation graph explicit.

## 7. Stage 2D result

Stage 2D defines

`E_X(P) = sum_A min_m [F_X(A,m) + lambda_c kappa(m)] + lambda_b B_X(P)`.

The geometric fit is normalized by cell cardinality and `diam(X)^2`; the boundary term is a normalized weighted cut over an explicit observation graph. The implementation is in `structure/theory_energy_model.py`, with regression contracts in `tests/test_theory_energy_model.py`.

This closes the **energy-functional boundary**, but it does not silently promote a universal plane/sphere/cylinder model family, graph-construction heuristic, or coefficient values.

## 8. Remaining closure target

The next mathematical target is now the **formation theorem**:

`P* in argmin_{P in A(X)} E_X(P)`

and, for a declared perturbation neighborhood,

`P* global minimizer => P* locally stable`.

The remaining open question is stronger:

`Stable + Minimal + admissibility => StructuralUnit`

and the existence/uniqueness conditions under which this implication is valid.

## 9. Release decision

Stage 2C remains **interface-complete** and Stage 2D is **energy-functional-complete at the declared parameterized boundary**. Neither stage claims the final Structural Unit existence/uniqueness theorem.

The governing rule remains:

`mathematical statement -> derivation/proof -> engineering implementation -> regression contract`.
