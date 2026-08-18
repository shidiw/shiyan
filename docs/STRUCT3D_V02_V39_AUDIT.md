# Struct3D v0.2–v3.9 Theory / Engineering Audit

## Scope

This audit cross-checks the frozen Struct3D mathematical specification, the historical engineering map in `Struct3D_工程代码.txt`, and the current theory-compliant core.

## 1. Historical chain

The engineering record establishes the historical sequence:

- v0.2 Primitive Structural Unit → `structure/unit.py`, `initialize.py`, `energy.py`
- v0.3 Structural Graph
- v0.4 Structural Refinement → graph/relation/refinement code
- v0.5 Structural Unit Discovery
- v0.6 Primitive Discovery
- v0.7 Primitive Energy
- v0.8 Hierarchy + Relation
- v1.0 World Model → Object / Instance / Relation / World modules
- v2.x invariance experiments
- v3.0 Canonical Structural World
- v3.1 Canonical Structural Identity
- v3.2 Structural Equivalence
- v3.3 Structural Isomorphism
- v3.4 Structural Automorphism
- v3.5 Structural Quotient
- v3.6 Canonical Structural Form
- v3.7 Structural Invariant
- v3.8 Structural Distance
- v3.9 Structural Matching

This confirms that Object/Instance/Hierarchy are historical engineering stages, but their existence in the engineering map alone does not make each one a frozen mathematical definition.

## 2. Frozen mathematical objects currently evidenced

The mathematical specification explicitly defines:

### Structural World

`W = (U, R, Phi)`.

### Structural Unit

`u_i = (G_i, theta_i)`.

### Structural Relation

`r_ij in R`, with relation construction not reducible to primitive-type equality; the stated evidence family is geometry + boundary + spatial information.

### Structural Graph

`G = (V, E)` with units as vertices and typed relations as edges.

### Relabeling / canonicalization

For a legal permutation `pi`, the specification requires canonicalization to satisfy:

`C(W) = C(pi(W))`.

### Structural Representation

`phi(W) in R^23` in the frozen v4.0 schema.

### Structural Distance

`D_R(W1,W2) = ||phi(W1)-phi(W2)||_2`.

The specification explicitly limits the zero-distance statement to equality in representation space unless injectivity is separately established.

## 3. What the current core is allowed to claim

The current theory-compliant implementation may claim:

- Unit and Relation are explicit mathematical objects.
- Graph domain constraints are enforced.
- World validates relation endpoints against its Unit domain.
- Canonical form is relabeling invariant under the implemented legal relabeling contract.
- The 23-dimensional representation schema is frozen.
- Distance is Euclidean distance in representation space.
- Matching is an argmin over an explicitly supplied admissible set.
- Object assembly is a derived construction when explicit assembly relations are supplied.

## 4. What the current core must NOT claim

The following are deliberately not promoted to frozen theorems merely because historical code exists:

1. A unique energy functional for all Struct3D Units.
2. A unique deterministic map `U -> R` without an explicit relation construction/evidence rule.
3. `Object = connected components` as a foundational theorem unless the mathematical specification explicitly defines it that way.
4. `Instance` as a theorem-level object when its mathematical definition is absent.
5. `Hierarchy` as a theorem-level object when its mathematical definition is absent.
6. `D_R = 0 => structural isomorphism` without representation injectivity.
7. Latent neural distance equality merely because an encoder is trained.

## 5. Important distinction: optimization vs stability

The current core separates:

`Pi_E* in argmin_{Pi in A} E(Pi)`

from a finite perturbation stability certificate. The latter is a test over an explicitly supplied perturbation family; it is not a theorem of global stability under arbitrary perturbations.

This prevents the implementation from silently turning an energy minimizer into a stronger stability theorem.

## 6. Object boundary decision

For the current theory-compliant stage, Object remains a **derived engineering construction** from explicit assembly relations. This is consistent with the current contract tests: assembly relations may merge units, non-assembly relations may not, and transitive closure is used only as the implementation of the derived assembly grouping.

If the mathematical specification later provides an explicit definition of Object, that definition must replace or formally justify this derived construction before Object is promoted to theorem-level status.

## 7. Audit status

### PASS — mathematical object/domain alignment

`Unit -> Relation -> Graph -> World` is aligned with the currently frozen definitions.

### PASS — historical isolation

Legacy implementations are retained as regression references and are not silently treated as mathematical axioms.

### PASS — invariance boundary

Canonicalization and representation invariance are tested without claiming injectivity.

### PASS — distance boundary

The current distance implementation matches the stated Euclidean representation-space definition.

### OPEN — constructive Unit emergence

The mathematical specification defines what a Unit is, but a complete theorem-level derivation from raw point cloud observations to the optimal/stable partition is not yet established by the specification currently available in the repository.

### OPEN — constructive Relation emergence

The specification states the relation object and evidence family, but does not yet provide a single executable relation-generation theorem that uniquely maps arbitrary Units to Relations.

### OPEN — Object theorem

Historical engineering contains Object code, but Object remains derived in the theory-compliant core until its formal mathematical definition is explicit.

### OPEN — Instance / Hierarchy theorem

These remain outside the frozen theorem-level core until their mathematical definitions are explicitly recovered from the authoritative theory.

## 8. Decision

Do not add more semantic hierarchy code at this stage. The next mathematically meaningful task is to recover and formalize the missing constructive statements for:

`observation -> admissible partitions -> Unit emergence`

and, separately,

`Units + explicit geometric/boundary/spatial evidence -> Relation`.

Only after those statements are explicit should Object/Instance/Hierarchy be promoted further.
