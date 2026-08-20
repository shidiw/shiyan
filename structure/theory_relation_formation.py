"""Stage 3 relation-formation contract for Struct3D.

A relation is formed only from an explicitly supplied admissibility predicate.
The frozen theory does not infer relations from primitive equality, distance
thresholds, connectivity, or other hidden heuristics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Optional, Sequence, Tuple

from .theory_core import TheoryUnit
from .theory_relation import StructuralRelation, StructuralRelations


RelationPredicate = Callable[[TheoryUnit, TheoryUnit], bool]


@dataclass(frozen=True)
class RelationEvidence:
    """Explicit evidence/provenance attached to a formed relation."""

    relation_type: str
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not self.relation_type:
            raise ValueError("relation_type must be non-empty")


def relation_is_admissible(
    source: TheoryUnit,
    target: TheoryUnit,
    predicate: RelationPredicate,
) -> bool:
    """Evaluate the supplied relation predicate, with no implicit heuristic."""
    if not callable(predicate):
        raise TypeError("predicate must be callable")
    return bool(predicate(source, target))


def form_relation(
    source: TheoryUnit,
    target: TheoryUnit,
    source_id: int,
    target_id: int,
    evidence: RelationEvidence,
    predicate: RelationPredicate,
) -> StructuralRelation:
    """Materialize one relation iff the explicit predicate admits the pair."""
    if not relation_is_admissible(source, target, predicate):
        raise ValueError("unit pair is not admissible under the supplied relation predicate")
    return StructuralRelation(
        source=source_id,
        target=target_id,
        relation_type=evidence.relation_type,
        evidence=dict(evidence.payload),
    )


def form_relations(
    units: Sequence[TheoryUnit],
    candidate_pairs: Sequence[Tuple[int, int]],
    evidence_factory: Callable[[int, int], RelationEvidence],
    predicate: RelationPredicate,
) -> StructuralRelations:
    """Form the exact relation set selected by an explicit predicate.

    Candidate pairs are an input to the theory boundary. Pairs rejected by the
    predicate are omitted; no additional pairs are inferred.
    """
    n = len(units)
    relations = []
    seen = set()
    for source_id, target_id in candidate_pairs:
        if not (0 <= source_id < n and 0 <= target_id < n):
            raise ValueError("candidate relation endpoint outside unit domain")
        if source_id == target_id:
            raise ValueError("relation endpoints must be distinct")
        key = (source_id, target_id)
        if key in seen:
            raise ValueError("duplicate candidate relation pair")
        seen.add(key)
        if relation_is_admissible(units[source_id], units[target_id], predicate):
            evidence = evidence_factory(source_id, target_id)
            relations.append(
                StructuralRelation(
                    source=source_id,
                    target=target_id,
                    relation_type=evidence.relation_type,
                    evidence=dict(evidence.payload),
                )
            )
    return StructuralRelations(relations=tuple(relations), unit_count=n)


__all__ = [
    "RelationEvidence",
    "RelationPredicate",
    "relation_is_admissible",
    "form_relation",
    "form_relations",
]
