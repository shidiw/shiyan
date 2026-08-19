# Struct3D Theory ↔ Engineering Deep Audit

Date: 2026-08-19
Branch: `refactor/theory-compliant-core`

## Purpose

This document is the direct comparison between the authoritative `Struct3D_数学理论.txt`, the historical engineering specification `Struct3D_工程实现.txt`, and the actual Python implementation on this branch.

It does **not** introduce new mathematics. It classifies existing code as theory-certified, a faithful container/scaffold, legacy engineering, or a theory gap.

## 1. Authoritative chain vs actual implementation

| Stage | Mathematical status | Engineering implementation | Verdict |
|---|---|---|---|
| Observation / raw geometry | historical v0.0 starting point | `data/`, `geometry/` | ENGINEERING INPUT; no frozen constructive theorem |
| Geometry → Energy | historical v0.0/v0.7 | `structure/energy.py` | LEGACY ONLY |
| Primitive Structural Unit | historical v0.2 | `structure/unit.py` | LEGACY ONLY; shape differs from frozen theory Unit |
| Structural Unit `u=(G,theta)` | frozen theory | `structure/theory_unit.py` / `TheoryUnit` alias | CERTIFIED CONTAINER |
| Partition | needed by historical Unit discovery | `structure/theory_core.py`, `theory_partition.py` | GENERIC SCAFFOLD; admissible-set construction is external |
| Structural Relation | frozen relation object | `structure/theory_relation.py` | CERTIFIED CONTAINER; construction rule remains external |
| Structural Graph `G=(V,E)` | frozen | `structure/theory_world.py` graph view | CERTIFIED |
| World `W=(U,R,Phi)` | frozen | `structure/theory_world.py` | CERTIFIED CONTAINER |
| Object assembly | historical engineering v1.x/v2.x | `assembly.py` plus theory derived assembly | DERIVED ENGINEERING; not a frozen theorem |
| Instance / Hierarchy | historical engineering | `hierarchy.py`, related modules | NOT FROZEN; do not promote |
| Relabeling equivalence | frozen | `theory_canonical.py` | CERTIFIED for finite worlds |
| Canonical form | frozen | exhaustive finite canonicalization | CERTIFIED |
| Structural invariant | frozen | `theory_invariant.py` with `I(W)=C(W)` | CERTIFIED canonical invariant |
| v4.0 representation | frozen only as a 23D grouped schema | `theory_representation_schema.py` | CERTIFIED SCHEMA; estimator not frozen |
| Structural Distance | frozen `||phi_1-phi_2||_2` | `theory_distance.py` | CERTIFIED representation-space distance |
| Structural Matching | frozen as minimization over admissible candidates | `theory_matching.py` | CERTIFIED GENERIC ARGMIN; final domain/cost remains external |
| Neural Struct3D | later engineering direction | neural objective modules | PROVISIONAL / PARTIAL; no theorem of latent metric equality |

## 2. The most important concrete mismatch: legacy Unit

The historical `structure/unit.py` defines a unit as an engineering object containing:

`points + primitive + indices + parameters + energy`.

The frozen mathematical Unit is:

`u_i = (G_i, theta_i)`.

Therefore the historical class must **not** be cited as the implementation of the theorem-level Unit. Its point storage, primitive label, fitted parameters, and cached energy are engineering state. The theory-compliant class is `structure/theory_unit.py`, where `indices` represent `G_i` and `attributes` represent `theta_i`; primitive is explicitly optional metadata.

This distinction is now deliberate rather than accidental.

## 3. Energy: historical code is not the frozen theory

`structure/energy.py` implements an additive functional of the form

`E_fit + lambda * E_complexity + gamma * E_boundary`.

It also contains primitive-specific fitting rules and a hard-coded primitive complexity mapping. The mathematical specification currently available in the repository does **not** freeze this functional as the universal Struct3D energy.

Accordingly:

- `structure/energy.py` = LEGACY regression implementation.
- `structure/theory_energy.py` = theory-safe external functional interface.
- No default energy weights are promoted into the mathematical theory.

This is a required boundary, not unfinished cleanup.

## 4. Unit emergence is the largest current theory gap

The engineering story says:

`geometry → energy → stable region → unit`.

The current frozen mathematical layer does not yet provide all ingredients needed for a theorem-level constructive map from raw observations to the optimal Unit partition:

1. an authoritative observation domain,
2. an admissible partition family,
3. a final energy functional,
4. a theorem establishing the selected partition as the intended Unit decomposition.

`theory_partition.py` therefore performs only the mathematically safe operation: argmin over an explicitly supplied finite admissible set.

It does **not** claim that the raw point cloud automatically produces that candidate set.

## 5. Relation emergence is also incomplete

The frozen theory defines a relation object and identifies geometry/boundary/spatial information as relevant evidence. The engineering code historically contains relation generation/refinement behavior, but the current mathematical contract does not yet define one unique executable relation constructor for arbitrary Units.

Therefore the theory layer accepts explicit relations and validates their domain; it does not infer edges from primitive equality or hidden heuristics.

## 6. Object / Instance / Hierarchy boundary

The historical engineering roadmap explicitly passes through Object, Instance, and Hierarchy. However, existence of those modules does not itself constitute a theorem-level mathematical definition.

Current rule:

- Object assembly may be used as a **derived construction** from explicit assembly relations.
- Instance is not promoted to a frozen theorem object.
- Hierarchy is not promoted to a frozen theorem object.

This prevents the engineering history from silently becoming mathematics.

## 7. Canonicalization is genuinely implemented

For a finite world, `theory_canonical.py` computes the lexicographically minimal serialization over all unit permutations. This directly realizes the frozen relabeling requirement:

`C(W) = C(pi(W))`.

`structurally_equivalent(a,b)` is equality of these canonical forms.

The implementation is exact for finite validation worlds, although exhaustive permutation is not a scalable production algorithm. Scalability is an engineering issue and must not be confused with mathematical validity of the finite definition.

## 8. Representation: 23 dimensions are frozen, feature formulas are not

The current code correctly freezes:

`phi(W) in R^23`

with group sizes:

`3 + 3 + 3 + 3 + 3 + 3 + 5 = 23`.

The code intentionally does not invent formulas for every coordinate. A concrete extractor is supplied externally and can be canonicalized through `represent_canonical`.

Therefore passing representation-schema tests proves the coordinate contract, not that an arbitrary extractor is structurally invariant or information-complete.

## 9. Structural Distance is implemented exactly at the representation level

The current definition is:

`D_R(W1,W2) = ||phi(W1)-phi(W2)||_2`.

The implementation checks finite coordinates and computes the Euclidean norm. The code and regression tests correctly avoid the invalid stronger statement:

`D_R=0 => W1 is structurally identical to W2`.

That implication requires injectivity of `phi` on structural equivalence classes and is not currently established.

## 10. Structural Matching is a generic optimization interface

The current matching implementation minimizes an explicitly supplied cost over an explicitly supplied admissible candidate set. It does not fabricate a correspondence and does not claim uniqueness under ties.

The historical engineering description of a richer matching cost is therefore classified as PARTIAL until that exact cost and admissible correspondence space are frozen by the mathematical specification.

## 11. Neural Struct3D boundary

The repository may define reconstruction and proposed distance/mutation objectives, but an encoder that empirically reconstructs `phi(W)` does not prove that latent Euclidean distance equals `D_R`.

The correct hierarchy is:

`W → phi(W) → D_R`

first, then a learned map `Z(W)` as a separate engineering hypothesis. A theorem such as

`||Z(W1)-Z(W2)||_2 = D_R(W1,W2)`

requires a distance-preservation guarantee and is not obtained merely by reconstruction training.

## 12. Final audit decision

### GREEN — directly aligned

- Structural Unit container
- Structural Relation container
- Structural Graph domain
- Structural World container
- Relabeling/canonical form
- Canonical invariant
- 23D representation schema
- Euclidean representation distance
- Generic admissible-set matching

### YELLOW — valid scaffold but not fully frozen

- concrete 23D feature extractor
- final matching cost
- neural distance-preserving objective/architecture
- derived Object assembly

### RED — do not use as mathematical evidence

- legacy additive energy implementation
- primitive-specific hard-coded complexity as a universal law
- legacy point/primitive/energy Unit class as the theorem-level Unit
- raw-point clustering thresholds as a proof of Unit emergence
- historical Instance/Hierarchy modules as theorem-level definitions

### OPEN THEORY WORK

The next mathematical work is not another neural module. It is to close the constructive chain:

`Observation → admissible partitions → Energy → Unit emergence`

and then define the executable relation constructor:

`Units + geometry/boundary/spatial evidence → Relations`.

Only after those are mathematically frozen should the historical Object → Instance → Hierarchy chain be promoted into the theorem-level Struct3D world model.
