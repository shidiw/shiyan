"""Theory-facing Structural Representation.

The low-level ``represent`` API remains available for historical callers. The
closed observation path is ``represent_observation`` / ``phi_x``: its 23
coordinates are deterministic finite statistics of one observation X and an
X-derived StructuralWorld. No learned feature extractor, semantic label, or
external coordinate function is required.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Sequence

from .theory_invariant import structural_invariant
from .theory_representation_schema import REPRESENTATION_DIM, group_slices, validate_grouped_representation
from .theory_world import StructuralWorld

RepresentationExtractor = Callable[[Any], Sequence[float]]


@dataclass(frozen=True)
class StructuralRepresentation:
    """A validated point of the frozen representation space R^23."""

    values: tuple[float, ...]

    def __post_init__(self) -> None:
        validate_grouped_representation(self.values)

    def as_tuple(self) -> tuple[float, ...]:
        return self.values

    @property
    def groups(self):
        slices = group_slices()
        return {name: self.values[sl] for name, sl in slices.items()}


def _build_representation(values: Sequence[float]) -> StructuralRepresentation:
    return StructuralRepresentation(tuple(float(v) for v in values))


def represent(world: StructuralWorld, extractor: RepresentationExtractor) -> StructuralRepresentation:
    """Legacy low-level representation boundary using an explicit extractor."""
    return _build_representation(extractor(world))


def represent_canonical(world: StructuralWorld, extractor: RepresentationExtractor) -> StructuralRepresentation:
    """Apply an explicit extractor to the frozen canonical invariant I(W)=C(W)."""
    return _build_representation(extractor(structural_invariant(world)))


def _histogram(values, bins: int):
    counts = [0.0] * bins
    for value in values:
        counts[int(value)] += 1.0
    total = float(len(values))
    return tuple(c / total for c in counts) if total else tuple(counts)


def _connected_components(world: StructuralWorld) -> int:
    n = world.unit_count
    if n == 0:
        return 0
    adjacency = [set() for _ in range(n)]
    for relation in world.relations:
        adjacency[relation.source].add(relation.target)
        adjacency[relation.target].add(relation.source)
    seen = set()
    components = 0
    for root in range(n):
        if root in seen:
            continue
        components += 1
        stack = [root]
        seen.add(root)
        while stack:
            current = stack.pop()
            for neighbor in adjacency[current]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
    return components


def _relation_confidence(relation) -> float:
    value = relation.evidence.get("confidence", 0.0)
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        numeric = 0.0
    return numeric if numeric == numeric and numeric not in (float("inf"), float("-inf")) else 0.0


def represent_observation(world: StructuralWorld, context) -> StructuralRepresentation:
    """Construct the frozen 23-D coordinate map Phi_X(W) from X-derived data."""
    n = len(context.observation.points)
    unit_count = world.unit_count
    relation_count = world.relation_count

    model_scores = []
    for unit in world.units:
        best_index = 0
        best_value = float("inf")
        for index, model in enumerate(context.model_family):
            total = 0.0
            for point_index in unit.indices:
                residual = float(model.squared_distance(context.observation.points[point_index]))
                total += residual
            score = total / (len(unit.indices) * context.observation.scale ** 2) + model.complexity
            if score < best_value:
                best_value = score
                best_index = index
        model_scores.append(best_index)
    primitive_histogram = _histogram(model_scores, 3)

    composition = []
    for unit in world.units:
        size = len(unit.indices)
        composition.append(0 if size == 1 else 2 if size == n else 1)
    object_composition_histogram = _histogram(composition, 3)

    non_singleton = sum(1 for unit in world.units if len(unit.indices) > 1)
    object_count_topology = (float(unit_count), float(non_singleton), float(_connected_components(world)))

    relation_type_counts = [0.0, 0.0, 0.0]
    for relation in world.relations:
        if relation.relation_type == "adjacent":
            relation_type_counts[0] += 1.0
        elif relation.relation_type == "proximity":
            relation_type_counts[1] += 1.0
        else:
            relation_type_counts[2] += 1.0
    relation_type_histogram = (
        tuple(v / relation_count for v in relation_type_counts)
        if relation_count else (0.0, 0.0, 0.0)
    )

    confidences = [_relation_confidence(r) for r in world.relations]
    relation_confidence_statistics = (
        (min(confidences), sum(confidences) / len(confidences), max(confidences))
        if confidences else (0.0, 0.0, 0.0)
    )

    occupancies = [len(unit.indices) / n for unit in world.units]
    instance_occupancy_statistics = (
        (min(occupancies), sum(occupancies) / len(occupancies), max(occupancies))
        if occupancies else (0.0, 0.0, 0.0)
    )

    relation_type_count = len({relation.relation_type for relation in world.relations})
    max_unit_size = max((len(unit.indices) for unit in world.units), default=0)
    global_structural_counts = (
        float(n),
        float(unit_count),
        float(relation_count),
        float(relation_type_count),
        float(max_unit_size),
    )

    values = (
        primitive_histogram
        + object_composition_histogram
        + object_count_topology
        + relation_type_histogram
        + relation_confidence_statistics
        + instance_occupancy_statistics
        + global_structural_counts
    )
    if len(values) != REPRESENTATION_DIM:
        raise AssertionError("Phi_X construction must produce exactly 23 coordinates")
    return _build_representation(values)


def phi_x(world: StructuralWorld, context) -> StructuralRepresentation:
    """Canonical name for the observation-derived representation Phi_X(W)."""
    return represent_observation(world, context)


__all__ = [
    "REPRESENTATION_DIM",
    "RepresentationExtractor",
    "StructuralRepresentation",
    "represent",
    "represent_canonical",
    "represent_observation",
    "phi_x",
]
