"""Observation-derived Struct3D theory objects.

This module closes the remaining engineering-input boundaries in the finite
observation core. Every object below is a deterministic function of X and uses
no semantic labels and no neural component:

    X -> A_max(X) -> Gamma(X)
      -> M(X) + G_B(X) + (N_X,S_X) + C_R(X)
      -> Stage 2D -> Unit -> Relation -> World -> Phi_X.

The ``ObservationDerivedContext`` is the single provenance carrier for this
closed path. Theory-facing stages should consume its derived objects rather
than independently accepting external candidate/model/boundary/relation/
representation providers.

All constructions are finite and permutation-compatible on the observation
index universe.
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
    return GeometricModel("point", lambda p, c=center: _distance(p, c) ** 2, 0.0)


def _line_model(points: Tuple[Point, ...]) -> GeometricModel:
    center = _centroid(points)
    variances = _axis_variances(points, center)
    axis = max(range(3), key=lambda k: (variances[k], -k))

    def residual(p: Point, c=center, a=axis) -> float:
        return sum((p[k] - c[k]) ** 2 for k in range(3) if k != a)

    return GeometricModel("line", residual, 1.0)


def _plane_model(points: Tuple[Point, ...]) -> GeometricModel:
    center = _centroid(points)
    variances = _axis_variances(points, center)
    normal = min(range(3), key=lambda k: (variances[k], k))

    def residual(p: Point, c=center, a=normal) -> float:
        return (p[a] - c[a]) ** 2

    return GeometricModel("plane", residual, 2.0)


@dataclass(frozen=True)
class ObservationModelFamily:
    """Finite model family M(X): point, line, and plane fitted to X."""

    observation: Observation3D
    models: Tuple[GeometricModel, ...]

    @classmethod
    def from_observation(cls, observation: Observation3D) -> "ObservationModelFamily":
        points = observation.points
        return cls(observation, (_point_model(points), _line_model(points), _plane_model(points)))


@dataclass(frozen=True)
class ObservationBoundaryGraph:
    """Observation-derived boundary graph G_B(X).

    Every unordered point pair is an edge with
    w_ij = 1 / (1 + ||x_i-x_j|| / diam(X)).
    """

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


def observation_neighborhood(candidate: StructuralUnit, observation: Observation3D) -> StabilityNeighborhood[StructuralUnit]:
    """Define N_X(candidate) by one-index insertion/deletion moves."""
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
    """Define S_X(candidate) as every non-empty proper support subset."""
    support = tuple(candidate.indices)
    if len(support) <= 1:
        return ()
    return tuple(
        StructuralUnit(subset, {})
        for size in range(1, len(support))
        for subset in combinations(support, size)
    )


def observation_unit_candidates(observation: Observation3D) -> Tuple[StructuralUnit, ...]:
    """Define the finite Unit-candidate family of all non-empty supports."""
    omega = tuple(range(len(observation.points)))
    return tuple(
        StructuralUnit(support, {})
        for size in range(1, len(omega) + 1)
        for support in combinations(omega, size)
    )


def observation_relation_candidates(unit_count: int) -> Tuple[Tuple[int, int], ...]:
    """Define C_R(X) as all ordered pairs of distinct materialized Units."""
    if unit_count < 0:
        raise ValueError("unit_count must be non-negative")
    return tuple((i, j) for i in range(unit_count) for j in range(unit_count) if i != j)


@dataclass(frozen=True)
class ObservationDerivedContext:
    """All formerly external theorem boundaries materialized from one X.

    This context is the canonical observation-derived interface. The six
    former boundaries are exposed as named projections:

    A_max/Gamma, M, G_B, N_X/S_X, C_R, and Phi_X.

    ``Stage2DEnergy``, relation formation, World construction, and Phi_X are
    reachable from this same context, preventing a theory-facing caller from
    silently substituting an external object at one of those boundaries.
    """

    observation: Observation3D
    candidates: ObservationCandidateFamily
    models: ObservationModelFamily
    boundary: ObservationBoundaryGraph

    @classmethod
    def from_points(cls, points: Sequence[Point]) -> "ObservationDerivedContext":
        observation = Observation3D(tuple(points))
        candidates = observation_candidate_family(observation.points)
        models = ObservationModelFamily.from_observation(observation)
        boundary = ObservationBoundaryGraph.from_observation(observation)
        return cls(observation, candidates, models, boundary)

    @property
    def a_max(self):
        return self.candidates.a_max

    @property
    def gamma(self):
        return self.candidates.gamma

    @property
    def model_family(self) -> Tuple[GeometricModel, ...]:
        return self.models.models

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
        return self.candidates.materialize()

    def stage2d_energy(
        self,
        *,
        lambda_complexity: float = 1.0,
        lambda_boundary: float = 1.0,
        separation_margin: float = 0.0,
    ) -> Stage2DEnergy:
        """Return the unique Stage 2D energy attached to this observation."""
        return Stage2DEnergy.from_observation(
            self,
            lambda_complexity=lambda_complexity,
            lambda_boundary=lambda_boundary,
            separation_margin=separation_margin,
        )

    def form_relations(self, units: Sequence[StructuralUnit]):
        """Return C_R(X)-derived relations for the supplied materialized Units."""
        from .theory_relation_formation import form_observation_relations

        return form_observation_relations(tuple(units), self)

    def build_world(self, partition: Partition):
        """Materialize W=(U,R,Phi) from an X-derived partition."""
        from .theory_world import StructuralWorld

        relations = self.form_relations(partition.units)
        return StructuralWorld(
            units=partition.units,
            relations=relations.relations,
            attributes={},
            observation_context=self,
        )

    def phi_x(self, world):
        """Return the observation-derived representation Phi_X(W)."""
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
