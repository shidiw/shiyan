"""End-to-end Struct3D theory pipeline.

The canonical observation-facing path is delegated to
``ObservationDerivedPipeline`` and therefore uses the first-class
ObservationDerivedBoundaries carrier: X -> A/Gamma/M/G_B/N_X/S_X/C_R/Phi_X
-> Stage 2D -> Unit -> World -> Representation.
Historical explicit-input APIs remain available only for regression
compatibility.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence, Tuple

from .theory_canonical import canonical_form
from .theory_core import Partition, StructuralUnit, evaluate_energy
from .theory_energy import StructuralEnergy
from .theory_energy_model import Observation3D, Stage2DEnergy
from .theory_observation import ObservationDerivedContext
from .theory_observation_pipeline import ObservationDerivedPipeline
from .theory_partition import PartitionSelection, select_minimum_energy_partition
from .theory_relation import StructuralRelation
from .theory_representation import StructuralRepresentation, represent
from .theory_world import StructuralWorld
from .theory_candidate_search import A_search


@dataclass(frozen=True)
class TheoryPipelineResult:
    partition_selection: PartitionSelection
    world: StructuralWorld
    canonical: object
    representation: StructuralRepresentation


def run_theory_pipeline(
    candidate_partitions: Sequence[Partition],
    energy: Callable[[Partition], float],
    relations: Sequence[StructuralRelation],
    representation_extractor: Callable[[StructuralWorld], Sequence[float]],
) -> TheoryPipelineResult:
    """Historical explicit-input compatibility path."""
    selection = select_minimum_energy_partition(candidate_partitions, StructuralEnergy(energy))
    partition = selection.partition
    world = StructuralWorld(units=partition.units, relations=tuple(relations), attributes={})
    return TheoryPipelineResult(selection, world, canonical_form(world), represent(world, representation_extractor))


def build_gamma(observation: Sequence[object]):
    """Return the observation-derived Gamma-family object."""
    return ObservationDerivedContext.from_points(tuple(observation)).candidates


def select_stage2d_partition(
    observation: Observation3D,
    energy: Stage2DEnergy,
    unit_builder: Callable[[Tuple[int, ...]], StructuralUnit] | None = None,
) -> Partition:
    """Compatibility API; canonical execution is observation-derived Stage 2E."""
    if energy.observation != observation:
        raise ValueError("Stage 2D energy must be defined on the supplied observation")
    context = ObservationDerivedContext.from_points(observation.points)
    pipeline = ObservationDerivedPipeline(context)
    if unit_builder is not None:
        candidates = tuple(
            Partition(
                units=tuple(unit_builder(unit.indices) for unit in partition.units),
                universe=partition.universe,
            )
            for partition in pipeline.partitions
        )
    else:
        candidates = pipeline.partitions
    if not candidates:
        raise ValueError("No observation-derived partition exists")
    return min(candidates, key=lambda partition: evaluate_energy(partition, energy))


def run_observation_derived_pipeline(
    points: Sequence[Tuple[float, float, float]],
) -> TheoryPipelineResult:
    """Canonical X -> boundaries -> Stage2D -> Unit -> Q_X -> World -> Phi_X path."""
    pipeline = ObservationDerivedPipeline.from_points(points)
    selection = select_minimum_energy_partition(
        pipeline.partitions,
        StructuralEnergy(pipeline.energy),
    )
    world = pipeline.world()
    return TheoryPipelineResult(selection, world, canonical_form(world), pipeline.representation())


__all__ = [
    "TheoryPipelineResult",
    "run_theory_pipeline",
    "run_observation_derived_pipeline",
    "build_gamma",
    "select_stage2d_partition",
]
