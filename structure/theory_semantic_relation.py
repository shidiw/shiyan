"""Materialization of the strong observation-derived Q_X relation set."""

from __future__ import annotations

from typing import Sequence

from .theory_relation import StructuralRelation, StructuralRelations
from .theory_semantic_observation import Q_X, Q_X_strength


def form_observation_semantic_relations(units: Sequence[object], context) -> StructuralRelations:
    """Materialize R_Q(X) using the frozen strong Q_X predicate."""
    relations = []
    n = len(units)
    for source_id in range(n):
        for target_id in range(n):
            if source_id == target_id:
                continue
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
