"""Materialization of the strong observation-derived Q_X relation set."""

from __future__ import annotations

from typing import Sequence

from .theory_relation import StructuralRelation, StructuralRelations
from .theory_semantic_observation import Q_X, Q_X_strength


def form_observation_semantic_relations(units: Sequence[object], context) -> StructuralRelations:
    """Materialize R_Q(X) from the unique observation-derived C_R(X) domain.

    The candidate relation domain is no longer re-created locally with
    ``range(n)``.  This makes C_R(X) an actual upstream theorem object consumed
    by Stage 3 rather than a descriptive duplicate of the implementation.
    """
    units = tuple(units)
    n = len(units)
    candidate_pairs = context.relation_candidates(n)
    expected = {(i, j) for i in range(n) for j in range(n) if i != j}
    if set(candidate_pairs) != expected:
        raise ValueError("Observation-derived C_R(X) must contain exactly all ordered distinct Unit pairs")

    relations = []
    for source_id, target_id in candidate_pairs:
        source = units[source_id]
        target = units[target_id]
        if not Q_X(source, target, context):
            continue
        relations.append(
            StructuralRelation(
                source=source_id,
                target=target_id,
                relation_type="semantic_proximity",
                evidence={
                    "rule": "Q_X: cross-support distance <= local median scale",
                    "strength": Q_X_strength(source, target, context),
                },
            )
        )
    return StructuralRelations(relations=tuple(relations), unit_count=n)


__all__ = ["form_observation_semantic_relations"]