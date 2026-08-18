# Struct3D Phase 2 — Math/Code Boundary

## Purpose

Phase 2 extends the already certified Unit/Relation/Graph/World core without silently promoting legacy engineering behavior into mathematics.

## Frozen mathematical objects

The current mathematical specification explicitly defines:

- Structural Unit: `u_i = (G_i, theta_i)`
- Structural Relation: `r_ij in R`
- Structural Graph: `G = (V, E)`
- Structural World: `W = (U, R, Phi)`
- Relabeling equivalence: `W ~_label pi(W)`
- Canonical form: `C(W) = C(pi(W))`
- Structural invariant: invariant under legal relabeling
- Representation: `phi(W) in R^23` with seven declared coordinate groups
- Structural distance: `D_R(W1,W2) = ||phi(W1)-phi(W2)||_2`
- Matching: an abstract minimum-cost correspondence framework

## Explicit theory gap

The current specification does **not** provide formal definitions for Object, Instance, or Hierarchy as separate mathematical objects, nor does it freeze a unique operator for Object emergence.

Therefore:

- `structure/theory_object.py` is a **derived engineering construction** only.
- `structure/instance.py` remains **legacy engineering code** and is not part of the certified theory core.
- `structure/hierarchy.py` remains **legacy engineering code** until the mathematical specification defines the corresponding object and axioms.
- No implementation may claim that `Object -> Instance -> Hierarchy` is a theorem of the current specification.

## Current derived Object rule

For engineering integration only, an explicit assembly relation subset may be used:

`O_derived = connected_components(U, R_assembly)`

This rule is deliberately not called a Struct3D theorem. It is deterministic, auditable, and contains no primitive-equality or distance-threshold inference.

## Phase 2 acceptance rule

Before adding an Instance or Hierarchy theory module, the mathematical specification must contain the corresponding definition. If it does not, the code remains an adapter/legacy layer and is tested only for isolation and non-interference with the certified core.
