"""Observation-derived Struct3D theory objects.

All theory-facing boundaries are deterministic functions of one finite
observation X.  No semantic labels and no neural component are used.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import sqrt
from typing import Sequence, Tuple

from .theory_candidates import ObservationCandidateFamily, observation_candidate_family
from .theory_candidate_search import Gamma_X, materialize_Gamma
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
        return self.observation == Observation3D(tuple(self.observation.points))


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


def observation_neighborhood(candidate: StructuralUnit, observation: Observation3D) -> StabilityNeighborhood[StructuralUnit]:
    """Frozen N_X: one-point insertion/deletion neighborhood derived from X."""
    omega = set(range(len(observation.points)))
    support = set(candidate.indices)
    alternatives = set()
    for index in tuple(support):
        reduced = tuple(sorted(support - {index}))
        if reduced:
            alternatives.add(reduced)
    for index in sorted(omega - support):
        alternatives.add(tuple(sorted(support | {index})))
    units = tuple(StructuralUnit(block, {}) for block in sorted(alternatives))
    if not units:
        units = (candidate,)
    return StabilityNeighborhood(units)


def observation_proper_subcandidates(candidate: StructuralUnit) -> Tuple[StructuralUnit, ...]:
    """Frozen S_X: scalable proper subcandidate family.

    It contains every one-point deletion and the singleton supports. This is a
    finite, non-empty-for-non-singletons, quotient-compatible local family and
    avoids enumerating the exponential full subset lattice.
    """
    support = tuple(candidate.indices)
    if len(support) <= 1:
        return ()
    subsets = {tuple(sorted(support[:k] + support[k + 1 :])) for k in range(len(support))}
    subsets.update((index,) for index in support)
    subsets.discard(support)
    return tuple(StructuralUnit(subset, {}) for subset in sorted(subsets))


def observation_unit_candidates(observation: Observation3D) -> Tuple[StructuralUnit, ...]:
    """Units appearing in the observation-derived computational family Gamma(X)."""
    unique = {}
    for partition in materialize_Gamma(observation):
        for unit in partition.units:
            unique[tuple(unit.indices)] = unit
    return tuple(unique[key] for key in sorted(unique))


def observation_relation_candidates(unit_count: int) -> Tuple[Tuple[int, int], ...]:
    if unit_count < 0:
        raise ValueError("unit_count must be non-negative")
    return tuple((i, j) for i in range(unit_count) for j in range(unit_count) if i != j)


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
    def a_max(self):
        return self.candidates.a_max

    @property
    def gamma(self):
        """Primary computational Gamma(X), a strict finite subset of A_max(X)."""
        return Gamma_X(self.observation)

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
        return observation_proper_subcandidates(candidate)

    def relation_candidates(self, unit_count: int) -> Tuple[Tuple[int, int], ...]:
        return observation_relation_candidates(unit_count)

    def materialize_partitions(self) -> Tuple[Partition, ...]:
        return materialize_Gamma(self.observation)

    def stage2d_energy(self) -> Stage2DEnergy:
        return Stage2DEnergy.from_observation(self)

    def form_relations(self, units: Sequence[StructuralUnit]):
        from .theory_relation_formation import form_observation_relations
        return form_observation_relations(tuple(units), self)

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


__all__ = [
    "ObservationModelFamily",
    "ObservationBoundaryGraph",
    "ObservationDerivedContext",
    "observation_neighborhood",
    "observation_proper_subcandidates",
    "observation_unit_candidates",
    "observation_relation_candidates",
]
