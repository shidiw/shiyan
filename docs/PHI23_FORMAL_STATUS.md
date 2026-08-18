# Struct3D v4.0: formal status of the 23-D representation

## Frozen mathematical statement

The current specification freezes

\[
\phi(W) = [h_P,h_O,t_O,h_R,s_R,o_I,g] \in \mathbb{R}^{23},
\]

with group sizes `3,3,3,3,3,3,5`.

## What is formally frozen

- the domain is a structural world `W`;
- the codomain is `R^23`;
- the seven coordinate groups and their dimensions;
- representation-space distance is the Euclidean norm of the resulting vectors.

## What is not formally frozen

The current mathematical specification does not uniquely define the numerical
estimator for each coordinate. Therefore the Theory Core does not silently
invent formulas for primitive histograms, object statistics, relation
statistics, instance occupancy, or global counts.

A concrete estimator must be supplied as an explicit extractor. It becomes a
candidate mathematical implementation only after its definition and required
invariance properties are formally specified and tested.

## Consequence

The following implication is intentionally *not* asserted by this module:

`arbitrary extractor -> relabeling-invariant representation`.

For a proposed extractor `F`, invariance must be established separately:

\[
F(\pi(W)) = F(W)
\]

for the permitted relabelings `\pi`.

Likewise, no injectivity claim is made:

\[
\phi(W_1)=\phi(W_2)
\]

does not by itself imply structural isomorphism.

This document is a theory boundary, not a new feature definition.
