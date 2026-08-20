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

The implementation now exposes the following chain without pretending that the missing mathematical inputs are solved:

`X`

`-> explicit admissible family A(X)`

`-> supplied energy E`

`-> explicit perturbation neighborhood N(A)`

`-> Stable(A)`

`-> explicit proper-subcandidate family`

`-> MinimalStable(A)`

`-> [future Unit-emergence theorem]`

`-> StructuralUnit`

The final implication is still a theory gap. The important change is that the gap is now represented by an explicit executable boundary rather than being hidden inside a function named `select_stable_partition`.

## 7. Next closure target

Stage 2D must now address the exact energy domain and the historical additive skeleton:

`E = E_fit + lambda_c C + lambda_b B`.

The next step is to determine, from the preserved mathematical source, which parts of `E_fit`, `C`, and `B` can be formally defined without importing the legacy primitive-specific implementation. Only after that audit can an exact energy functional be promoted into theory-facing code.

## 8. Release decision

Stage 2C is **implementation-complete as a boundary** when the new regression file passes together with the existing suite. It is **not** a claim that the upstream Structural Unit existence theorem is complete.

The governing rule remains:

`mathematical statement -> derivation/proof -> engineering implementation -> regression contract`.
