"""Observation-derived Struct3D theory objects.

Canonical provenance is generated from one finite observation X.  The module
owns the observation-derived boundaries A_max/Gamma, M, G_B, N_X, S_X and
C_R.  No semantic labels, neural parameters, or caller-supplied mathematical
objects are required on the canonical path.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import sqrt
from typing import Sequence, Tuple

from .theory_candidates import ObservationCandidateFamily, observation_candidate_family
from .theory_core import Partition, StructuralUnit
from .theory_energy_model import GeometricModel, Observation3D, Stage2DEnergy, WeightedObservationGraph
from .theory_stability import StabilityNeighborhood

Point = Tuple[float, float, float]


def _distance(a: Point, b: Point) -> float:
    return sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _centroid(points: Sequence[Point]) -> Point:
    n = len(points)
    return tuple(sum(p[k] for p in points) / n for k in range(3))  # type: ignore[return-value]


def _axis_variances(points: Sequence[Point], center: Point) -> Tuple[float, float, float]:
    n = len(points)
    return tuple(sum((p[k] - center[k]) ** 2 for p in points) / n for k in range(3))  # type: ignore[return-value]


def _point_model(points: Tuple[Point, ...]) -> GeometricModel:
    center = _centroid(points)
    return GeometricModel("point", lambda p, c=center: _distance(p, c) ** 2, 0.0, signature=("point", center))


def _line_model(points: Tuple[Point, ...]) -> GeometricModel:
    center = _centroid(points)
    variances = _axis_variances(points, center)
    axis = max(range(3), key=lambda k: (variances[k], -k))

    def residual(p: Point, c=center, a=axis) -> float:
        return sum((p[k] - c[k]) ** 2 for k in range(3) if k != a)

    return GeometricModel("line", residual, 1.0, signature=("line", center, axis))


def _plane_model(points: Tuple[Point, ...]) -> GeometricModel:
    center = _centroid(points)
    variances = _axis_variances(points, center)
    normal = min(range(3), key=lambda k: (variances[k], k))

    def residual(p: Point, c=center, a=normal) -> float:
        return (p[a] - c[a]) ** 2

    return GeometricModel("plane", residual, 2.0, signature=("plane", center, normal))


@dataclass(frozen=True)
class ObservationModelFamily:
    """Frozen observation-derived model universe M(X)."""

    observation: Observation3D
    models: Tuple[GeometricModel, ...]

    @classmethod
    def from_observation(cls, observation: Observation3D) -> "ObservationModelFamily":
        points = observation.points
        return cls(observation, (_point_model(points), _line_model(points), _plane_model(points)))

    @property
    def universe(self) -> Tuple[GeometricModel, ...]:
        return self.models

    def is_deterministic_for(self, observation: Observation3D) -> bool:
        return self == ObservationModelFamily.from_observation(observation)

    def is_quotient_compatible(self) -> bool:
        return self == ObservationModelFamily.from_observation(self.observation)


@dataclass(frozen=True)
class ObservationBoundaryGraph:
    """Frozen observation-derived complete boundary graph G_B(X)."""

    observation: Observation3D
    graph: WeightedObservationGraph

    @classmethod
    def from_observation(cls, observation: Observation3D) -> "ObservationBoundaryGraph":
        scale = observation.scale
        edges = []
        for i, j in combinations(range(len(observation.points)), 2):
            distance = _distance(observation.points[i], observation.points[j])
            edges.append((i, j, 1.0 / (1.0 + distance / scale)))
        if len(observation.points) == 1:
            graph = WeightedObservationGraph((), universe_size=1, allow_zero_total=True)
        else:
            graph = WeightedObservationGraph(tuple(edges), universe_size=len(observation.points))
        return cls(observation, graph)

    @property
    def total_weight(self) -> float:
        return self.graph.total_weight

    @property
    def is_complete(self) -> bool:
        n = len(self.observation.points)
        return len(self.graph.edges) == n * (n - 1) // 2

    def is_quotient_compatible(self) -> bool:
        return self.is_complete


def _validate_support(candidate: StructuralUnit, observation: Observation3D) -> Tuple[int, ...]:
    omega = set(range(len(observation.points)))
    support = tuple(sorted(candidate.indices))
    if not support or any(index not in omega for index in support):
        raise ValueError("Unit support must be a non-empty subset of the observation universe")
    return support


def observation_neighborhood(candidate: StructuralUnit, observation: Observation3D) -> StabilityNeighborhood[StructuralUnit]:
    """Frozen N_X: one-point insertion/deletion neighborhood derived from X."""
    support = set(_validate_support(candidate, observation))
    omega = set(range(len(observation.points)))
    alternatives = set()
    for index in support:
        reduced = tuple(sorted(support - {index}))
        if reduced:
            alternatives.add(reduced)
    for index in sorted(omega - support):
        alternatives.add(tuple(sorted(support | {index})))
    units = tuple(StructuralUnit(block, {}) for block in sorted(alternatives))
    if not units:
        units = (candidate,)
    return StabilityNeighborhood(units)


def observation_proper_subcandidates(
    candidate: StructuralUnit,
    observation: Observation3D | None = None,
) -> Tuple[StructuralUnit, ...]:
    """Frozen S_X: every non-empty proper support subset of the candidate."""
    if observation is not None:
        support = _validate_support(candidate, observation)
    else:
        support = tuple(sorted(candidate.indices))
        if not support:
            raise ValueError("Unit support must be non-empty")
    subsets = []
    for size in range(1, len(support)):
        subsets.extend(combinations(support, size))
    return tuple(StructuralUnit(tuple(subset), {}) for subset in subsets)


def observation_unit_candidates(observation: Observation3D) -> Tuple[StructuralUnit, ...]:
    """All non-empty support Units induced by the finite observation universe."""
    indices = tuple(range(len(observation.points)))
    return tuple(
        StructuralUnit(tuple(subset), {})
        for size in range(1, len(indices) + 1)
        for subset in combinations(indices, size)
    )


def observation_relation_candidates(unit_count: int) -> Tuple[Tuple[int, int], ...]:
    """Compatibility projection of the complete ordered pair domain."""
    if unit_count < 0:
        raise ValueError("unit_count must be non-negative")
    return tuple((i, j) for i in range(unit_count) for j in range(unit_count) if i != j)


@dataclass(frozen=True)
class ObservationRelationCandidateDomain:
    """Observation-derived candidate relation domain C_R(X)."""

    observation: Observation3D
    units: Tuple[StructuralUnit, ...]
    pairs: Tuple[Tuple[int, int], ...]

    @classmethod
    def from_observation(
        cls,
        observation: Observation3D,
        units: Sequence[StructuralUnit],
    ) -> "ObservationRelationCandidateDomain":
        normalized = tuple(units)
        for unit in normalized:
            _validate_support(unit, observation)
        pairs = observation_relation_candidates(len(normalized))
        return cls(observation, normalized, pairs)

    def __len__(self) -> int:
        return len(self.pairs)

    def __iter__(self):
        return iter(self.pairs)

    def __contains__(self, pair) -> bool:
        return pair in self.pairs

    @property
    def finite(self) -> bool:
        return True

    @property
    def complete_ordered(self) -> bool:
        n = len(self.units)
        return len(self.pairs) == n * (n - 1)

    def is_quotient_compatible(self) -> bool:
        return self.complete_ordered


@dataclass(frozen=True)
class ObservationDerivedContext:
    """Single X-derived provenance carrier for the closed theory-facing path."""

    observation: Observation3D
    candidates: ObservationCandidateFamily
    models: ObservationModelFamily
    boundary: ObservationBoundaryGraph

    @classmethod
    def from_points(cls, points: Sequence[Point]) -> "ObservationDerivedContext":
        observation = Observation3D(tuple(points))
        return cls(
            observation,
            observation_candidate_family(observation.points),
            ObservationModelFamily.from_observation(observation),
            ObservationBoundaryGraph.from_observation(observation),
        )

    @property
    def omega(self) -> Tuple[int, ...]:
        return tuple(range(len(self.observation.points)))

    @property
    def a_max(self):
        return self.candidates.a_max

    @property
    def gamma(self):
        """Canonical Gamma(X), frozen equal to the complete A_max(X)."""
        return self.candidates.gamma

    @property
    def model_family(self) -> Tuple[GeometricModel, ...]:
        return self.models.universe

    @property
    def boundary_graph(self) -> WeightedObservationGraph:
        return self.boundary.graph

    @property
    def unit_candidates(self) -> Tuple[StructuralUnit, ...]:
        return observation_unit_candidates(self.observation)

    def neighborhood_rule(self, candidate: StructuralUnit) -> StabilityNeighborhood[StructuralUnit]:
        return observation_neighborhood(candidate, self.observation)

    def proper_subcandidates(self, candidate: StructuralUnit) -> Tuple[StructuralUnit, ...]:
        return observation_proper_subcandidates(candidate, self.observation)

    def relation_domain(self, units: Sequence[StructuralUnit]) -> ObservationRelationCandidateDomain:
        return ObservationRelationCandidateDomain.from_observation(self.observation, units)

    def relation_candidates(self, unit_count: int) -> Tuple[Tuple[int, int], ...]:
        return observation_relation_candidates(unit_count)

    def materialize_partitions(self) -> Tuple[Partition, ...]:
        """Materialize the canonical Gamma(X)=A_max(X) family."""
        return self.candidates.materialize()

    def stage2d_energy(self) -> Stage2DEnergy:
        return Stage2DEnergy.from_observation(self)

    def prove_stage2e_existence(self, *, require_strict_margin: bool = False):
        """Run the observation-derived Stage 2E existence theorem from this X."""
        from .theory_stage2e_existence import prove_observation_derived_stage2e_existence
        return prove_observation_derived_stage2e_existence(self, require_strict_margin=require_strict_margin)

    def form_relations(self, units: Sequence[StructuralUnit]):
        from .theory_semantic_relation import form_observation_semantic_relations
        return form_observation_semantic_relations(tuple(units), self)

    def build_world(self, partition: Partition):
        from .theory_world import StructuralWorld
        relations = self.form_relations(partition.units)
        return StructuralWorld(
            units=partition.units,
            relations=relations.relations,
            attributes={},
            observation_context=self,
        )

    def phi_x(self, world):
        from .theory_representation import phi_x
        return phi_x(world, self)

    def representation_map(self):
        """Return the first-class observation-derived Phi_X map."""
        from .theory_observation_pipeline import ObservationRepresentationMap
        return ObservationRepresentationMap(self)


__all__ = [
    "ObservationModelFamily",
    "ObservationBoundaryGraph",
    "ObservationRelationCandidateDomain",
    "ObservationDerivedContext",
    "observation_neighborhood",
    "observation_proper_subcandidates",
    "observation_unit_candidates",
    "observation_relation_candidates",
]
