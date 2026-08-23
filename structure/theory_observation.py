"""Observation-derived Struct3D theory objects.

This module closes the remaining *engineering input* boundaries in the frozen
finite-observation core.  Every object below is a deterministic function of the
observation X and contains no semantic labels and no neural component:

    X -> A_max(X) -> Gamma(X)
      -> M(X) + G_B(X) + (N_X,S_X) + C_R(X)
      -> Stage 2D -> Unit -> Relation -> World -> Phi_X.

The definitions are deliberately finite.  They are also invariant under a
permutation of observation indices because they are built from sets, pairwise
Euclidean distances, support cardinalities, and canonical sorting only.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import isfinite, sqrt
from typing import Callable, Sequence, Tuple

from .theory_candidates import ObservationCandidateFamily, observation_candidate_family
from .theory_core import Partition, StructuralUnit
from .theory_energy_model import GeometricModel, Observation3D, WeightedObservationGraph
from .theory_stability import StabilityNeighborhood

Point = Tuple[float, float, float]
Block = Tuple[int, ...]


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
    return GeometricModel(
        "point",
        squared_distance=lambda p, c=center: _distance(p, c) ** 2,
        complexity=0.0,
    )


def _line_model(points: Tuple[Point, ...]) -> GeometricModel:
    center = _centroid(points)
    variances = _axis_variances(points, center)
    axis = max(range(3), key=lambda k: (variances[k], -k))

    def residual(p: Point, c=center, a=axis) -> float:
        # Distance to the affine coordinate line c + t e_a.
        return sum((p[k] - c[k]) ** 2 for k in range(3) if k != a)

    return GeometricModel("line", squared_distance=residual, complexity=1.0)


def _plane_model(points: Tuple[Point, ...]) -> GeometricModel:
    center = _centroid(points)
    variances = _axis_variances(points, center)
    normal = min(range(3), key=lambda k: (variances[k], k))

    def residual(p: Point, c=center, a=normal) -> float:
        # Distance to the affine coordinate plane c + span{e_j : j != a}.
        return (p[a] - c[a]) ** 2

    return GeometricModel("plane", squared_distance=residual, complexity=2.0)


@dataclass(frozen=True)
class ObservationModelFamily:
    """The finite model family M(X) derived directly from X.

    The family contains three canonical affine model classes fitted to X:
    point, line, and plane.  Complexity is the affine dimension (0, 1, 2).
    No primitive label or user-selected model is required.
    """

    observation: Observation3D
    models: Tuple[GeometricModel, ...]

    @classmethod
    def from_observation(cls, observation: Observation3D) -> "ObservationModelFamily":
        points = observation.points
        return cls(observation, (_point_model(points), _line_model(points), _plane_model(points)))


@dataclass(frozen=True)
class ObservationBoundaryGraph:
    """Observation-derived boundary graph G_B(X).

    Every unordered pair of observation points is an edge.  Its weight is

        w_ij = 1 / (1 + ||x_i-x_j|| / diam(X)).

    Hence every weight is strictly positive for distinct points and the graph
    is finite, connected, and free of an externally supplied threshold.
    """

    observation: Observation3D
    graph: WeightedObservationGraph

    @classmethod
    def from_observation(cls, observation: Observation3D) -> "ObservationBoundaryGraph":
        scale = observation.scale
        edges = []
        for i, j in combinations(range(len(observation.points)), 2):
            distance = _distance(observation.points[i], observation.points[j])
            weight = 1.0 / (1.0 + distance / scale)
            edges.append((i, j, weight))
        # A one-point observation has no cut edges.  The Stage 2D energy model
        # accepts this as the unique zero-boundary case.
        if len(observation.points) == 1:
            graph = WeightedObservationGraph((), universe_size=1, allow_zero_total=True)
        else:
            graph = WeightedObservationGraph(tuple(edges), universe_size=len(observation.points))
        return cls(observation, graph)


def observation_neighborhood(candidate: StructuralUnit, observation: Observation3D) -> StabilityNeighborhood[StructuralUnit]:
    """Define N_X(candidate) by one-index insertion/deletion moves.

    The neighborhood is finite and depends only on the observation index
    universe and the candidate support.  It contains the candidate itself when
    no other move exists, satisfying the executable neighborhood contract for
    singleton observations.
    """
    omega = set(range(len(observation.points)))
    support = set(candidate.indices)
    alternatives = set()

    for index in tuple(support):
        reduced = tuple(sorted(support - {index}))
        if reduced:
            alternatives.add(reduced)
    for index in sorted(omega - support):
        expanded = tuple(sorted(support | {index}))
        alternatives.add(expanded)

    units = tuple(StructuralUnit(indices=block, attributes={}) for block in sorted(alternatives))
    if not units:
        units = (candidate,)
    return StabilityNeighborhood(units)


def observation_proper_subcandidates(candidate: StructuralUnit) -> Tuple[StructuralUnit, ...]:
    """Define S_X(candidate) as all non-empty proper support subsets."""
    support = tuple(candidate.indices)
    if len(support) <= 1:
        return ()
    result = []
    for size in range(1, len(support)):
        for subset in combinations(support, size):
            result.append(StructuralUnit(indices=subset, attributes={}))
    return tuple(result)


def observation_relation_candidates(unit_count: int) -> Tuple[Tuple[int, int], ...]:
    """Define C_R(X) on any materialized X-derived world as all ordered unit pairs."""
    if unit_count < 0:
        raise ValueError("unit_count must be non-negative")
    return tuple((i, j) for i in range(unit_count) for j in range(unit_count) if i != j)


@dataclass(frozen=True)
class ObservationDerivedContext:
    """All formerly external theorem boundaries materialized from one X."""

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

    def neighborhood_rule(self, candidate: StructuralUnit) -> StabilityNeighborhood[StructuralUnit]:
        return observation_neighborhood(candidate, self.observation)

    def proper_subcandidates(self, candidate: StructuralUnit) -> Tuple[StructuralUnit, ...]:
        return observation_proper_subcandidates(candidate)

    def relation_candidates(self, unit_count: int) -> Tuple[Tuple[int, int], ...]:
        return observation_relation_candidates(unit_count)

    def materialize_partitions(self) -> Tuple[Partition, ...]:
        return self.candidates.materialize()


__all__ = [
    "ObservationModelFamily",
    "ObservationBoundaryGraph",
    "ObservationDerivedContext",
    "observation_neighborhood",
    "observation_proper_subcandidates",
    "observation_relation_candidates",
]
