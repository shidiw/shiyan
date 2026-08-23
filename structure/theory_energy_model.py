"""Stage 2D: explicit and observation-derived mathematical energy models.

For a finite observation X={x_i} and a partition P={A_j}, the frozen
observation-derived energy is

    E_X(P) = sum_A e_X(A) + B_X(P),

where

    e_X(A) = min_{m in M(X)} F_X(A,m) + k(m),

    F_X(A,m) = 1/(|A| s(X)^2) sum_{i in A} d(x_i,M_m)^2,

and

    B_X(P) = cut_w(P) / total_w.

The complexity and boundary weights are frozen constants equal to one in the
observation-derived theory. They are therefore not external theorem degrees
of freedom. The separation margin is also not an input: the canonical
observation-derived margin is the minimum positive energy gap between
quotient-distinct members of the finite candidate family. A theorem requiring
strict separation may test that derived quantity is positive.

The historical explicit-input constructor remains available for low-level
regression compatibility; theory-facing execution must use
``Stage2DEnergy.from_observation(context)``.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Callable, Optional, Tuple

from .theory_core import Partition, StructuralUnit

Point = Tuple[float, float, float]
Residual = Callable[[Point], float]


def _freeze(value: Any):
    if isinstance(value, dict):
        return tuple(sorted((str(k), _freeze(v)) for k, v in value.items()))
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(v) for v in value)
    if isinstance(value, set):
        return tuple(sorted((_freeze(v) for v in value), key=repr))
    try:
        hash(value)
        return value
    except TypeError:
        return repr(value)


def unit_quotient_key(unit: StructuralUnit):
    return (tuple(unit.indices), _freeze(unit.attributes))


def partition_quotient_key(partition: Partition):
    unit_keys = tuple(sorted((unit_quotient_key(unit) for unit in partition.units), key=repr))
    return (tuple(partition.universe), unit_keys)


def structurally_equivalent_partitions(a: Partition, b: Partition) -> bool:
    return partition_quotient_key(a, b) == partition_quotient_key(b, a)


@dataclass(frozen=True)
class SeparationMarginResult:
    requested_margin: float
    minimum_gap: float
    compared_pairs: int
    satisfied: bool


@dataclass(frozen=True)
class ObservationEnergyParameters:
    """Canonical Stage 2D parameters derived from X.

    The values are frozen dimensionless constants. Their provenance is the
    observation-derived energy definition itself, not caller-selected
    hyperparameters.
    """

    lambda_complexity: float = 1.0
    lambda_boundary: float = 1.0

    @classmethod
    def from_observation(cls, observation: "Observation3D") -> "ObservationEnergyParameters":
        if not observation.points:
            raise ValueError("Observation must be non-empty")
        return cls()


@dataclass(frozen=True)
class Observation3D:
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
        maximum = 0.0
        for i, a in enumerate(self.points):
            for b in self.points[i + 1 :]:
                distance = math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
                maximum = max(maximum, distance)
        return maximum


@dataclass(frozen=True)
class GeometricModel:
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
    edges: Tuple[Tuple[int, int, float], ...]
    universe_size: int
    allow_zero_total: bool = False

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
        if total <= 0.0 and not (self.allow_zero_total and self.universe_size == 1 and not self.edges):
            raise ValueError("Boundary graph must have positive total edge weight")

    @property
    def total_weight(self) -> float:
        return sum(float(weight) for _, _, weight in self.edges)


@dataclass(frozen=True)
class Stage2DEnergy:
    observation: Observation3D
    models: Tuple[GeometricModel, ...]
    boundary_graph: WeightedObservationGraph
    lambda_complexity: float = 1.0
    lambda_boundary: float = 1.0
    separation_margin: float = 0.0
    observation_context: Any = None

    def __post_init__(self) -> None:
        if not self.models:
            raise ValueError("At least one geometric model is required")
        if self.boundary_graph.universe_size != len(self.observation.points):
            raise ValueError("Boundary graph and observation universes must agree")
        if (
            not math.isfinite(float(self.lambda_complexity))
            or not math.isfinite(float(self.lambda_boundary))
            or not math.isfinite(float(self.separation_margin))
        ):
            raise ValueError("Energy weights and separation margin must be finite")
        if self.lambda_complexity < 0.0 or self.lambda_boundary < 0.0:
            raise ValueError("Energy weights must be non-negative")
        if self.separation_margin < 0.0:
            raise ValueError("Separation margin must be non-negative")

    @classmethod
    def from_observation(cls, context) -> "Stage2DEnergy":
        """Construct the canonical E_X directly from observation-derived M(X), G_B(X)."""
        parameters = ObservationEnergyParameters.from_observation(context.observation)
        return cls(
            observation=context.observation,
            models=tuple(context.model_family),
            boundary_graph=context.boundary_graph,
            lambda_complexity=parameters.lambda_complexity,
            lambda_boundary=parameters.lambda_boundary,
            separation_margin=0.0,
            observation_context=context,
        )

    def _validate_partition_universe(self, partition: Partition) -> None:
        expected = tuple(range(len(self.observation.points)))
        if partition.universe != expected:
            raise ValueError("Partition universe must match observation indices exactly")

    @staticmethod
    def _validate_margin(margin: float) -> float:
        value = float(margin)
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError("A theorem-level separation margin must be finite and positive")
        return value

    def fit_energy(self, unit: StructuralUnit, model: GeometricModel) -> float:
        indices = unit.indices
        if not indices:
            raise ValueError("Unit support must be non-empty")
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
        if self.boundary_graph.total_weight <= 0.0:
            return 0.0
        labels = {}
        for unit_index, unit in enumerate(partition.units):
            for point_index in unit.indices:
                labels[point_index] = unit_index
        cut = 0.0
        for source, target, weight in self.boundary_graph.edges:
            if labels[source] != labels[target]:
                cut += float(weight)
        return cut / self.boundary_graph.total_weight

    def energy_gap(self, a: Partition, b: Partition) -> float:
        self._validate_partition_universe(a)
        self._validate_partition_universe(b)
        if structurally_equivalent_partitions(a, b):
            return 0.0
        return abs(float(self(a)) - float(self(b)))

    def derived_separation_margin(self, candidates: Tuple[Partition, ...]) -> float:
        """Return delta_X, the minimum positive quotient-distinct energy gap.

        No caller supplies delta. The value is a deterministic finite statistic
        of X through the canonical finite candidate family and E_X. It is zero
        exactly when quotient-distinct candidates are energy-tied.
        """
        minimum_gap = math.inf
        for i, first in enumerate(candidates):
            first_energy = float(self(first))
            for second in candidates[i + 1 :]:
                if structurally_equivalent_partitions(first, second):
                    continue
                gap = abs(first_energy - float(self(second)))
                if gap > 0.0:
                    minimum_gap = min(minimum_gap, gap)
        return 0.0 if minimum_gap is math.inf else minimum_gap

    def verify_derived_separation(self, candidates: Tuple[Partition, ...]) -> SeparationMarginResult:
        derived = self.derived_separation_margin(candidates)
        compared_pairs = 0
        for i, first in enumerate(candidates):
            for second in candidates[i + 1 :]:
                if not structurally_equivalent_partitions(first, second):
                    compared_pairs += 1
        return SeparationMarginResult(derived, derived, compared_pairs, derived > 0.0)

    def verify_separation_margin(
        self,
        candidates: Tuple[Partition, ...],
        margin: Optional[float] = None,
    ) -> SeparationMarginResult:
        """Verify an explicitly requested margin for generic regression use.

        Theory-facing code should use ``verify_derived_separation`` instead.
        """
        requested = self.separation_margin if margin is None else float(margin)
        requested = self._validate_margin(requested)
        minimum_gap = math.inf
        compared_pairs = 0
        for i, first in enumerate(candidates):
            first_energy = float(self(first))
            if not math.isfinite(first_energy):
                raise ValueError("Candidate energy must be finite")
            for second in candidates[i + 1 :]:
                if structurally_equivalent_partitions(first, second):
                    continue
                second_energy = float(self(second))
                if not math.isfinite(second_energy):
                    raise ValueError("Candidate energy must be finite")
                compared_pairs += 1
                minimum_gap = min(minimum_gap, abs(first_energy - second_energy))
        satisfied = minimum_gap >= requested
        return SeparationMarginResult(requested, minimum_gap, compared_pairs, satisfied)

    def require_separation_margin(
        self,
        candidates: Tuple[Partition, ...],
        margin: Optional[float] = None,
    ) -> SeparationMarginResult:
        result = self.verify_separation_margin(candidates, margin)
        if not result.satisfied:
            raise ValueError(
                "Stage 2D separation margin is not satisfied: "
                f"minimum_gap={result.minimum_gap}, required={result.requested_margin}"
            )
        return result

    def __call__(self, partition: Partition) -> float:
        self._validate_partition_universe(partition)
        fit_and_complexity = sum(self.unit_energy(unit) for unit in partition.units)
        return fit_and_complexity + self.lambda_boundary * self.boundary_energy(partition)


__all__ = [
    "Observation3D",
    "GeometricModel",
    "WeightedObservationGraph",
    "ObservationEnergyParameters",
    "SeparationMarginResult",
    "unit_quotient_key",
    "partition_quotient_key",
    "structurally_equivalent_partitions",
    "Stage2DEnergy",
]
