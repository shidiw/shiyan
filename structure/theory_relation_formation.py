"""Stage 3 relation-formation contracts for Struct3D.

Stage 3A keeps relation formation explicit: a relation is materialized only
when a supplied admissibility predicate accepts a candidate pair.

Stage 3B adds one frozen geometry-derived predicate for 3-D supports:

    Q_adj(G_i, G_j) = 1  iff  H^2(boundary(G_i) ∩ boundary(G_j)) > 0.

The predicate expresses positive-area boundary contact. It is invariant under
unit relabeling and rigid motions because Hausdorff measure and set
intersection are invariant under isometries. The implementation receives the
pairwise geometric measure as evidence; it does not approximate Hausdorff
measure from a hidden threshold or nearest-neighbour heuristic.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Callable, Mapping, Sequence, Tuple

from .theory_core import TheoryUnit
from .theory_relation import StructuralRelation, StructuralRelations


RelationPredicate = Callable[[TheoryUnit, TheoryUnit], bool]
CandidateRelationPredicate = Callable[[int, int], bool]


@dataclass(frozen=True)
class RelationEvidence:
    """Explicit evidence/provenance attached to a formed relation."""

    relation_type: str
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not self.relation_type:
            raise ValueError("relation_type must be non-empty")


@dataclass(frozen=True)
class GeometryRelationEvidence:
    """Pairwise geometric evidence for the Stage 3B adjacency predicate."""

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


def relation_is_admissible(
    source: TheoryUnit,
    target: TheoryUnit,
    predicate: RelationPredicate,
) -> bool:
    """Evaluate the supplied unit-level relation predicate."""
    if not callable(predicate):
        raise TypeError("predicate must be callable")
    return bool(predicate(source, target))


def geometry_adjacency_q(evidence: GeometryRelationEvidence) -> bool:
    """Return the frozen Stage 3B predicate H^2(∂G_i ∩ ∂G_j) > 0."""
    return evidence.boundary_contact_measure > 0.0


def geometry_adjacency_predicate(
    evidence_by_pair: Mapping[Tuple[int, int], GeometryRelationEvidence],
) -> CandidateRelationPredicate:
    """Build an index-level Q predicate from explicit geometric evidence."""
    normalized = dict(evidence_by_pair)

    def predicate(source_id: int, target_id: int) -> bool:
        evidence = normalized.get((source_id, target_id))
        if evidence is None:
            return False
        return geometry_adjacency_q(evidence)

    return predicate


def form_geometry_relations(
    units: Sequence[TheoryUnit],
    candidate_pairs: Sequence[Tuple[int, int]],
    evidence_by_pair: Mapping[Tuple[int, int], GeometryRelationEvidence],
) -> StructuralRelations:
    """Form `adjacent` relations using explicit pair-indexed evidence."""
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
    """Materialize one relation iff the explicit unit-level predicate admits it."""
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
    """Form exactly the admitted relations among the supplied candidate pairs.

    The candidate-level predicate receives the explicit integer pair `(i, j)`.
    This is intentional: candidate-domain restriction is a statement about the
    admissible index set, not about hidden geometry or Unit attributes.
    """
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
]
