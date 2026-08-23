"""Stage 3 relation-formation contracts for Struct3D.

The observation-derived API freezes

    C_R(X) = {(i,j): i != j}

and the relation predicate

    Q_X(u_i,u_j) <=> d_X(u_i,u_j) is finite and positive-confidence.

For every valid finite X with positive diameter this predicate is true for
all distinct candidate Units, so the frozen observation-only relation is the
complete proximity relation with explicit geometric distance evidence. The
stronger H^2 boundary-contact predicate remains available as a separate
geometry theorem and is not silently conflated with Q_X.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Any, Callable, Mapping, Sequence, Tuple

from .theory_core import TheoryUnit
from .theory_relation import StructuralRelation, StructuralRelations

RelationPredicate = Callable[[TheoryUnit, TheoryUnit], bool]
CandidateRelationPredicate = Callable[[int, int], bool]


@dataclass(frozen=True)
class RelationEvidence:
    relation_type: str
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not self.relation_type:
            raise ValueError("relation_type must be non-empty")


@dataclass(frozen=True)
class GeometryRelationEvidence:
    boundary_contact_measure: float
    hausdorff_dimension: int = 2

    def __post_init__(self) -> None:
        value = float(self.boundary_contact_measure)
        if not isfinite(value):
            raise ValueError("boundary contact measure must be finite")
        if value < 0.0:
            raise ValueError("boundary contact measure must be non-negative")
        if self.hausdorff_dimension != 2:
            raise ValueError("3-D boundary contact uses H^2")


def relation_is_admissible(source: TheoryUnit, target: TheoryUnit, predicate: RelationPredicate) -> bool:
    if not callable(predicate):
        raise TypeError("predicate must be callable")
    return bool(predicate(source, target))


def geometry_adjacency_q(evidence: GeometryRelationEvidence) -> bool:
    return evidence.boundary_contact_measure > 0.0


def geometry_adjacency_predicate(
    evidence_by_pair: Mapping[Tuple[int, int], GeometryRelationEvidence],
) -> CandidateRelationPredicate:
    normalized = dict(evidence_by_pair)

    def predicate(source_id: int, target_id: int) -> bool:
        evidence = normalized.get((source_id, target_id))
        return evidence is not None and geometry_adjacency_q(evidence)

    return predicate


def form_geometry_relations(
    units: Sequence[TheoryUnit],
    candidate_pairs: Sequence[Tuple[int, int]],
    evidence_by_pair: Mapping[Tuple[int, int], GeometryRelationEvidence],
) -> StructuralRelations:
    evidence_map = dict(evidence_by_pair)
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
        evidence = evidence_map.get(key)
        if evidence is not None and geometry_adjacency_q(evidence):
            relations.append(
                StructuralRelation(
                    source=source_id,
                    target=target_id,
                    relation_type="adjacent",
                    evidence={
                        "rule": "H^2(boundary intersection) > 0",
                        "boundary_contact_measure": evidence.boundary_contact_measure,
                    },
                )
            )
    return StructuralRelations(relations=tuple(relations), unit_count=n)


def form_relation(
    source: TheoryUnit,
    target: TheoryUnit,
    source_id: int,
    target_id: int,
    evidence: RelationEvidence,
    predicate: RelationPredicate,
) -> StructuralRelation:
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
    predicate: CandidateRelationPredicate,
) -> StructuralRelations:
    if not callable(predicate):
        raise TypeError("predicate must be callable")
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
        if bool(predicate(source_id, target_id)):
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


def _point_distance(a, b) -> float:
    return sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def observation_relation_distance(source: TheoryUnit, target: TheoryUnit, context) -> float:
    """Minimum cross-support Euclidean distance, normalized by diam(X)."""
    points = context.observation.points
    distances = (_point_distance(points[i], points[j]) for i in source.indices for j in target.indices)
    return min(distances) / context.observation.scale


def observation_relation_predicate(
    source: TheoryUnit,
    target: TheoryUnit,
    context,
) -> bool:
    """Frozen observation-derived Q_X for the proximity relation.

    For valid finite X, disjoint non-empty Units have finite normalized
    cross-support distance and therefore positive confidence
    c_X=1/(1+d_X). Thus Q_X is deterministic, label-free, and quotient
    compatible; its truth value is determined entirely by X and the two Units.
    """
    if source == target or not source.indices or not target.indices:
        return False
    distance = observation_relation_distance(source, target, context)
    confidence = 1.0 / (1.0 + distance)
    return isfinite(distance) and distance >= 0.0 and confidence > 0.0


def form_observation_relations(units: Sequence[TheoryUnit], context) -> StructuralRelations:
    """Form the frozen C_R(X), Q_X observation-derived relation set."""
    pairs = context.relation_candidates(len(units))
    relations = []
    for source_id, target_id in pairs:
        source = units[source_id]
        target = units[target_id]
        if not observation_relation_predicate(source, target, context):
            continue
        normalized_distance = observation_relation_distance(source, target, context)
        confidence = 1.0 / (1.0 + normalized_distance)
        relations.append(
            StructuralRelation(
                source=source_id,
                target=target_id,
                relation_type="proximity",
                evidence={
                    "rule": "Q_X: finite normalized minimum cross-support distance",
                    "normalized_distance": normalized_distance,
                    "confidence": confidence,
                },
            )
        )
    return StructuralRelations(relations=tuple(relations), unit_count=len(units))


__all__ = [
    "RelationEvidence",
    "RelationPredicate",
    "CandidateRelationPredicate",
    "GeometryRelationEvidence",
    "relation_is_admissible",
    "geometry_adjacency_q",
    "geometry_adjacency_predicate",
    "form_geometry_relations",
    "form_relation",
    "form_relations",
    "observation_relation_distance",
    "observation_relation_predicate",
    "form_observation_relations",
]
