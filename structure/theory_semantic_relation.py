"""Materialization of the strong observation-derived Q_X relation set."""

from __future__ import annotations

from typing import Optional, Sequence

from .theory_relation import StructuralRelation, StructuralRelations
from .theory_semantic_observation import Q_X, Q_X_strength


def form_observation_semantic_relations(
    units: Sequence[object],
    context,
    candidate_domain=None,
) -> StructuralRelations:
    """Materialize R_Q(X) over the X-derived C_R(X) domain.

    ``candidate_domain`` is retained only as a compatibility hook.  The
    canonical observation-facing path never supplies it: C_R(X) is derived
    from ``context`` and the selected X-derived Units itself.
    """
    normalized_units = tuple(units)
    domain = candidate_domain if candidate_domain is not None else context.relation_domain(normalized_units)
    if tuple(domain.units) != normalized_units:
        raise ValueError("Relation candidate domain must be generated from the exact Unit sequence")

    relations = []
    for source_id, target_id in domain.pairs:
        source = normalized_units[source_id]
        target = normalized_units[target_id]
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
    return StructuralRelations(relations=tuple(relations), unit_count=len(normalized_units))


__all__ = ["form_observation_semantic_relations"]
