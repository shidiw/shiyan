"""Stage 2D: explicit mathematical energy model for Struct3D.

This module is a *newly derived closure proposal* built on the historical
skeleton

    E = E_fit + lambda_c C + lambda_b B.

It is not presented as a recovery of the old primitive-specific implementation.
All geometric model classes and the observation adjacency graph are explicit
inputs. Consequently the theory fixes the functional form and normalization
without silently freezing plane/sphere/cylinder heuristics, point-count
thresholds, or legacy boundary surrogates.

For a finite observation X={x_i} and a partition P={A_j}, define

    e(A) = min_{m in M} [ F(A,m) + lambda_c k(m) ]

with

    F(A,m) = 1/(|A| s(X)^2) sum_{i in A} d(x_i,M_m)^2,

and

    B(P) = cut_w(P) / total_w.

The partition energy is

    E(P) = sum_A e(A) + lambda_b B(P).

Here s(X)=diam(X) is a scale normalizer, k(m)>=0 is an explicitly supplied
model-complexity functional, and the weighted observation graph supplies the
boundary term. The model family and graph are part of the mathematical input,
not inferred by this module.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Tuple

from .theory_core import Partition, StructuralUnit

Point = Tuple[float, float, float]
Residual = Callable[[Point], float]


@dataclass(frozen=True)
class Observation3D:
    """Finite 3-D observation with a positive geometric scale."""

    points: Tuple[Point, ...]

    def __post_init__(self) -> None:
        if not self.points:
            raise ValueError("Observation must contain at least one point")
        normalized = []
        for point in self.points:
            if len(point) != 3:
                raise ValueError("Observation points must be three-dimensional")
            values = tuple(float(v) for v in point)
            if not all(math.isfinite(v) for v in values):
                raise ValueError("Observation coordinates must be finite")
            normalized.append(values)
        object.__setattr__(self, "points", tuple(normalized))
        if self.scale <= 0.0:
            raise ValueError("Observation diameter must be positive")

    @property
    def scale(self) -> float:
        """Diameter of the finite observation set."""
        maximum = 0.0
        for i, a in enumerate(self.points):
            for b in self.points[i + 1 :]:
                distance = math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
                maximum = max(maximum, distance)
        return maximum


@dataclass(frozen=True)
class GeometricModel:
    """An explicit geometric model used only by the Stage 2D functional."""

    name: str
    squared_distance: Residual
    complexity: float

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Geometric model name must be non-empty")
        if not math.isfinite(float(self.complexity)) or self.complexity < 0.0:
            raise ValueError("Model complexity must be finite and non-negative")


@dataclass(frozen=True)
class WeightedObservationGraph:
    """Explicit weighted graph used for the boundary term."""

    edges: Tuple[Tuple[int, int, float], ...]
    universe_size: int

    def __post_init__(self) -> None:
        if self.universe_size <= 0:
            raise ValueError("Graph universe must be non-empty")
        total = 0.0
        seen = set()
        for source, target, weight in self.edges:
            if source == target:
                raise ValueError("Boundary graph edges must connect distinct vertices")
            if not (0 <= source < self.universe_size and 0 <= target < self.universe_size):
                raise ValueError("Boundary edge lies outside graph universe")
            key = (source, target)
            if key in seen:
                raise ValueError("Boundary graph edges must not contain duplicate ordered pairs")
            seen.add(key)
            if not math.isfinite(float(weight)) or weight < 0.0:
                raise ValueError("Boundary edge weights must be finite and non-negative")
            total += float(weight)
        if total <= 0.0:
            raise ValueError("Boundary graph must have positive total edge weight")

    @property
    def total_weight(self) -> float:
        return sum(float(weight) for _, _, weight in self.edges)


@dataclass(frozen=True)
class Stage2DEnergy:
    """Dimensionless normalized realization of the historical energy skeleton."""

    observation: Observation3D
    models: Tuple[GeometricModel, ...]
    boundary_graph: WeightedObservationGraph
    lambda_complexity: float = 1.0
    lambda_boundary: float = 1.0

    def __post_init__(self) -> None:
        if not self.models:
            raise ValueError("At least one geometric model is required")
        if self.boundary_graph.universe_size != len(self.observation.points):
            raise ValueError("Boundary graph and observation universes must agree")
        if not math.isfinite(float(self.lambda_complexity)) or not math.isfinite(float(self.lambda_boundary)):
            raise ValueError("Energy weights must be finite")
        if self.lambda_complexity < 0.0 or self.lambda_boundary < 0.0:
            raise ValueError("Energy weights must be non-negative")

    def _validate_partition_universe(self, partition: Partition) -> None:
        expected = tuple(range(len(self.observation.points)))
        if partition.universe != expected:
            raise ValueError("Partition universe must match observation indices exactly")

    def fit_energy(self, unit: StructuralUnit, model: GeometricModel) -> float:
        indices = unit.indices
        if any(i < 0 or i >= len(self.observation.points) for i in indices):
            raise ValueError("Unit index lies outside the observation")
        total = 0.0
        for index in indices:
            residual = float(model.squared_distance(self.observation.points[index]))
            if not math.isfinite(residual) or residual < 0.0:
                raise ValueError("Model squared distance must be finite and non-negative")
            total += residual
        return total / (len(indices) * self.observation.scale ** 2)

    def unit_energy(self, unit: StructuralUnit) -> float:
        best = math.inf
        for model in self.models:
            fit = self.fit_energy(unit, model)
            value = fit + self.lambda_complexity * model.complexity
            if value < best:
                best = value
        if not math.isfinite(best):
            raise ValueError("Unit energy is not finite")
        return best

    def boundary_energy(self, partition: Partition) -> float:
        self._validate_partition_universe(partition)
        labels = {}
        for unit_index, unit in enumerate(partition.units):
            for point_index in unit.indices:
                labels[point_index] = unit_index
        cut = 0.0
        for source, target, weight in self.boundary_graph.edges:
            if labels[source] != labels[target]:
                cut += float(weight)
        return cut / self.boundary_graph.total_weight

    def __call__(self, partition: Partition) -> float:
        self._validate_partition_universe(partition)
        fit_and_complexity = sum(self.unit_energy(unit) for unit in partition.units)
        return fit_and_complexity + self.lambda_boundary * self.boundary_energy(partition)


__all__ = [
    "Observation3D",
    "GeometricModel",
    "WeightedObservationGraph",
    "Stage2DEnergy",
]
