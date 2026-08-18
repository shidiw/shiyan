# Struct3D Theory-Compliant Refactor Report

## Scope

This report records the completed theory-facing refactor on
`refactor/theory-compliant-core`. `main` remains untouched.

## Frozen theory used as the authority

The repository's `Struct3D_数学理论.txt` is treated as the specification.
It freezes the chain:

`W -> X -> structural graph -> canonical form -> invariant -> phi(W) in R^23 -> D_R -> matching -> neural structural geometry`.

It also explicitly distinguishes confirmed mathematics from proposed later
objectives. In particular, the exact v1.1 neural loss is not retroactively
claimed as v1.0.

## What changed

### 1. Unit / Partition core

Added `theory_core.py`.

- Structural Unit follows `u=(G, theta)`.
- Primitive is optional metadata, not the definition of a Unit.
- Partition requires non-empty, pairwise-disjoint, complete coverage.
- No primitive-specific or threshold-based assumptions are embedded.

### 2. Energy

Added `theory_energy.py`.

- Energy is an explicit functional supplied by the formal theory.
- No additive decomposition is invented.
- No default weights or regularizers are introduced.
- Existing `energy.py` remains legacy for regression comparison.

### 3. Stable Partition

Added `theory_partition.py`.

- Implements the operational `argmin` over an explicit admissible candidate set.
- Does not generate the candidate set.
- Does not use graph thresholds or minimum-size filters.
- Tie handling is deterministic but is not presented as mathematical uniqueness.

### 4. Relation

Added `theory_relation.py`.

- Implements `r_ij` as an explicit relation record.
- Evidence is explicit and provenance-carrying.
- Relation type is supplied rather than inferred from primitive equality or an unapproved threshold.
- Existing `relation.py` remains legacy.

### 5. Object / Assembly

Added `theory_object.py`.

- Object formation is the connected-component construction of an explicitly supplied assembly-relation graph.
- The module does not decide which geometric relation is an assembly relation.

### 6. Structural World

Added `theory_world.py`.

- Implements the frozen definition `W=(U,R,Phi)`.
- Validates relation indices against the unit domain.

### 7. Canonical form

Added `theory_canonical.py`.

- Defines canonical form as the lexicographically minimal finite serialization over all unit relabelings.
- This is exact for finite worlds; it is intentionally not presented as a scalable canonicalization algorithm.
- Large-world optimization remains an engineering task, not a hidden approximation.

### 8. Representation / Distance / Matching

Added:

- `theory_representation.py`
- `theory_distance.py`
- `theory_matching.py`

The representation dimension is fixed at 23. The actual feature extractor remains an explicit input so the code does not invent semantics for the 23 statistics.

Structural Distance is exactly:

`D_R(W1,W2) = ||phi(W1)-phi(W2)||_2`.

Matching is an explicit optimization over an admissible matching set and an explicit cost function. The historical document does not freeze one final cost decomposition, so none is invented here.

### 9. Neural Struct3D objective layer

Added `theory_neural.py`.

- Keeps reconstruction separate from the later distance-preserving direction.
- Implements the representation-distance mismatch and mutation-collapse penalty as explicit objective components.
- Does not prescribe network architecture or hyperparameters.

### 10. End-to-end composition

Added `theory_pipeline.py` to compose:

`candidate partitions -> energy minimization -> world -> canonical form -> 23D representation`.

## Regression coverage

Added tests for:

- runtime metadata
- legacy Energy / Unit behavior
- Unit and Partition invariants
- theory Energy interface
- stable Partition selection
- Relation / Object / World invariants
- canonical relabeling invariance
- 23D Representation
- Structural Distance symmetry and zero self-distance
- Matching argmin behavior
- neural objective components
- end-to-end theory pipeline

## Legacy policy

The following historical implementations remain untouched and are treated as
legacy until the formal specification proves their replacement:

- `structure/energy.py`
- `structure/graph_cluster.py`
- `structure/unit.py`
- `structure/relation.py`
- `structure/assembly.py`
- `structure/hierarchy.py`
- other historical world/instance/embedding modules

This prevents accidental rewriting of experimental history.

## Validation limitation

The repository was inspected and modified through GitHub. A local test run was
attempted from the public branch, but this execution environment cannot resolve
`github.com`, so the test suite could not be executed here. The branch therefore
must be run in the user's actual Struct3D environment before any claim of full
runtime validation is made.

## Main branch safety

Comparison against `main` shows the refactor branch is ahead of the main commit
`239f04cddbbd560777409de28b46d3e5400fc1f0` and has no commits behind it. No
changes were made directly to `main`.
