# Struct3D Global Mathematical Closure Audit

Branch: `refactor/theory-compliant-core`

## 1. Audit rule

The preserved `Struct3D_数学理论.txt` remains authoritative for what is already frozen. Historical engineering code is evidence, not a theorem. Newly derived closure stages are allowed only when they are explicitly labeled as extensions and accompanied by a mathematical statement, derivation, implementation contract, and regression tests.

## 2. Full chain verdict

`X -> A(X) -> E_X -> argmin -> stability -> minimality -> Unit -> Relation -> Graph -> World -> Canonical Form -> Invariant -> phi -> D_R -> Matching -> Neural`

| Link | Verdict | Reason |
|---|---|---|
| `X -> A(X)` | **OPEN** | No source-defined universal generator for admissible partitions from raw observations. |
| `A(X) -> P*` | **CLOSED CONDITIONALLY** | Finite, non-empty explicit candidate family plus finite energy gives an attained argmin. |
| `E` | **DERIVED EXTENSION** | Stage 2D supplies a normalized parameterized functional; it is not recovered historical theory. |
| `P* -> Stable` | **CLOSED CONDITIONALLY** | A global minimizer is locally stable for every explicitly supplied neighborhood contained in the admissible family. |
| `Stable -> MinimalStable` | **OPEN AS UNIVERSAL THEOREM / CLOSED AS INTERFACE** | Minimality depends on an explicit proper-subcandidate family. |
| `MinimalStable -> Unit` | **OPEN** | No source-backed theorem yet identifies every stable/minimal candidate with the foundational Unit. |
| `Unit -> Relation` | **DERIVED BOUNDARY** | Stage 3A accepts explicit candidates/predicates; Stage 3B supplies an optional Hausdorff-contact predicate using explicit evidence. |
| `Relation -> Graph` | **CLOSED** | Graph edges are copied from supplied relations. |
| `Graph -> World` | **CLOSED** | `W=(U,R,Phi)` is implemented as a validated container. |
| `World -> Canonical` | **CLOSED FOR FINITE REGIME** | Exhaustive finite relabeling canonicalization is exact for the declared validation regime. |
| `Canonical -> Invariant` | **CLOSED** | Frozen choice `I(W)=C(W)`. |
| `Invariant -> phi in R^23` | **BOUNDARY** | Dimension/grouping are frozen; numerical feature formulas are not universally derived. |
| `phi -> D_R` | **CLOSED** | Exact Euclidean representation-space distance. |
| `D_R -> Matching` | **CLOSED GENERICALLY** | Explicit admissible correspondence set and supplied cost are minimized. |
| `phi -> neural latent metric` | **OPEN** | Reconstruction or empirical correlation does not prove latent metric equality. |

## 3. Stage 2 closure audit

### 3.1 Admissibility

The valid partition object is closed. The generator `X -> A(X)` is not. The implementation therefore keeps candidate generation external and rejects the promotion of thresholds, connectivity, primitive classifiers, or minimum-size rules into the theorem layer.

### 3.2 Energy

The preserved historical skeleton is

`E = E_fit + lambda_c C + lambda_b B`.

Stage 2D derives the parameterized functional

`E_X(P) = sum_A min_{m in M} [F_X(A,m) + lambda_c kappa(m)] + lambda_b B_X(P)`

with diameter normalization and a normalized weighted cut. This is a mathematically explicit extension, not a historical recovery. The legacy `structure/energy.py` remains regression-only.

### 3.3 Stability

The executable local predicate is

`Stable(A;N,E) <=> E(A) <= E(B) for every B in N(A)`.

The neighborhood is an explicit input. No hidden geometry or threshold rule is inferred.

### 3.4 Minimality

The executable boundary is

`MinimalStable(A) <=> Stable(A) and no supplied proper subcandidate is Stable`.

This is an explicit conditional interface, not a universal theorem that raw geometry necessarily supplies the required subcandidate family.

### 3.5 Existence and uniqueness

Stage 2F proves existence only under a finite non-empty admissible family and finite energy. Stage 2G proves uniqueness only when the candidate has strictly smaller energy than every distinct competitor. Deterministic tie-breaking is never called uniqueness.

## 4. Stage 3 closure audit

Stage 3A is a generic relation-formation boundary:

`R_Q = { r_ij : (i,j) in C_R, Q(i,j)=True }`.

Stage 3B adds a separately labeled derived predicate for 3-D supports:

`Q_adj(G_i,G_j)=1 iff H^2(boundary(G_i) intersection boundary(G_j)) > 0`.

The code receives the pairwise Hausdorff-contact measure as explicit evidence. It does not estimate it from a hidden distance threshold. This closes the executable predicate boundary but does **not** prove that this is the unique universal relation law for all Struct3D scenes.

## 5. Downstream audit

- `C(W)` is exact for finite validation worlds.
- `I(W)=C(W)` is the frozen finite invariant.
- `phi(W) in R^23` is a validated coordinate schema.
- `D_R=||phi(W1)-phi(W2)||_2` is a true metric on representation points, but only a pseudometric on structural worlds unless representation injectivity is proved.
- Matching is a generic finite/admissible argmin.
- Neural objectives remain training contracts, not proofs of latent metric preservation.

## 6. Concrete engineering corrections in this audit pass

1. Generic theory energy evaluation now rejects `NaN` **and** positive/negative infinity, matching the finite-energy hypothesis of Stage 2F.
2. Stage 2D geometric fit now rejects negative observation indices instead of accidentally indexing from the end of a Python tuple.
3. Stage 2D weighted observation graphs now reject duplicate ordered edges, preventing accidental double-counting of the declared graph measure.
4. Neural objective weights and supplied loss terms now require finite real values, preventing non-finite training objectives from entering the theory-facing contract.
5. Regression tests were strengthened for all four boundaries.
6. The math-to-code map now distinguishes preserved frozen theory from Stage 2D/3B derived extensions.

## 7. Remaining blockers before claiming a fully closed raw-observation theory

Only these blockers remain at the theorem level:

1. **Admissible-family construction:** a source-backed or explicitly adopted definition of `X -> A(X)`.
2. **Unit-emergence theorem:** a theorem connecting admissibility + energy + stability + minimality to the foundational Structural Unit.
3. **Concrete representation formulas:** mathematical definitions for all seven groups of `phi`, plus proof of the intended invariance and any injectivity/completeness claim actually needed.
4. **Universal relation construction:** decide whether Stage 3B is adopted as the canonical relation predicate or remains one admissible relation type among several, and prove the required invariance properties.
5. **Neural distance preservation:** if claimed, it requires a separate theorem or a precisely bounded empirical statement; reconstruction alone is insufficient.

Object, Instance, and Hierarchy remain blocked until the foundational upstream chain is closed and their own definitions/invariance results are supplied.

## 8. Final release interpretation

The branch can be described as **theory-contract clean** when its regression suite passes. It must not yet be described as a universally closed Struct3D theorem from raw point cloud to learned structural metric.

The mathematically honest closed core is:

`explicit finite observation domain -> explicit admissible candidate family -> conditional argmin -> explicit stability/minimality predicates -> StructuralUnit container -> explicit Relations -> Graph -> World -> Canonical Form -> Invariant -> R^23 representation contract -> D_R -> generic Matching -> neural training contract`.

The next research theorem is therefore the upstream formation theorem, not another ungrounded neural module.
