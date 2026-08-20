# Struct3D Mathematical Closure — Stage 3: Relation Formation

## 1. Scope

Stage 3 closes the boundary between already-materialized Structural Units and
an explicit Structural Relation set.

The frozen world is still

`W = (U, R, Phi)`

and the graph remains

`G = (V, E)`

with vertices indexed by Units and edges copied exactly from `R`.

## 2. Relation admissibility

For Units `u_i, u_j`, define an explicitly supplied relation predicate

`Q(u_i, u_j) in {False, True}`.

A pair is admissible exactly when

`Q(u_i, u_j) = True`.

The predicate is mathematical input to the relation-formation boundary. It is
not silently instantiated by primitive equality, Euclidean proximity,
connectivity, curvature thresholds, or any other historical heuristic.

## 3. Candidate pair domain

Let `C_R` be an explicitly supplied finite set of ordered distinct index pairs:

`C_R subset {(i,j): 0 <= i,j < |U|, i != j}`.

The formed relation set is exactly

`R_Q = { r_ij : (i,j) in C_R and Q(u_i,u_j)=True }`.

Each relation carries an explicit type and evidence/provenance record.

No pair outside `C_R` can be added by the formation operator.

## 4. Formation rule

For an evidence record `e_ij=(type,payload)`,

`Form_Q(u_i,u_j) = r_ij`

iff `(i,j) in C_R` and `Q(u_i,u_j)=True`.

Otherwise no relation is materialized for that pair.

The endpoint constraints are part of the contract: endpoints must be distinct
and lie in the Unit domain.

## 5. Exact graph consequence

Once `R_Q` is formed,

`V = {0,...,|U|-1}`

and

`E = R_Q`.

Therefore the graph constructor is not a second inference mechanism. It is an
exact view of the formed relation set.

## 6. What is now closed

The following engineering behaviors are now explicit and testable:

1. a relation requires an explicit admissibility predicate;
2. rejected candidate pairs produce no relation;
3. accepted pairs materialize with supplied type/evidence;
4. candidate endpoints are domain-checked;
5. self-relations are rejected;
6. duplicate candidate pairs are rejected;
7. no hidden relation inference occurs outside the candidate set.

## 7. What remains a genuine theory problem

Stage 3 does **not** claim a universal formula for `Q` from raw geometry.
A future theory may define a geometry-derived relation predicate, but that
predicate must itself be stated and justified before it is promoted to frozen
theory.

Stage 3 also does not assert symmetry, transitivity, or completeness of the
relation graph. Those are additional properties requiring hypotheses or
separate definitions.

## 8. Closed chain

The current theory-facing chain is therefore

`X -> explicit A(X) -> E -> stable/minimal candidate -> Unit -> explicit C_R,Q -> Relation set R -> Graph G -> World W`.

The downstream canonical, invariant, representation, and distance layers may
consume `W`, but must not back-propagate an unproved relation rule into Stage 3.

## Verdict

**Stage 3 relation formation is implementation-closed as an explicit predicate
boundary. A universal geometry-to-relation theorem remains intentionally open.**
