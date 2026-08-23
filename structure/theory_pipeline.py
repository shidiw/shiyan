"""End-to-end theory-facing Struct3D pipeline.

Two paths are exposed:

* the historical low-level path with explicit inputs, retained for regression;
* the closed observation-derived path ``run_observation_derived_pipeline``.

The latter consumes one X-derived context for candidates, models, boundary,
relations, and representation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence, Tuple

from .theory_canonical import canonical_form
from .theory_candidates import ObservationCandidateFamily, observation_candidate_family
from .theory_core import Partition, TheoryUnit, evaluate_energy, StructuralUnit
from .theory_energy import StructuralEnergy
from .theory_energy_model import Observation3D, Stage2DEnergy
from .theory_partition import PartitionSelection, select_stable_partition
from .theory_relation import StructuralRelation
from .theory_relation_formation import form_observation_relations
from .theory_representation import StructuralRepresentation, represent, phi_x
from .theory_observation import ObservationDerivedContext
from .theory_world import StructuralWorld


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
    selection = select_stable_partition(candidate_partitions, StructuralEnergy(energy))
    partition = selection.partition
    world = StructuralWorld(units=partition.units, relations=tuple(relations), attributes={})
    return TheoryPipelineResult(
        partition_selection=selection,
        world=world,
        canonical=canonical_form(world),
        representation=represent(world, representation_extractor),
    )


def build_gamma(observation: Sequence[object]) -> ObservationCandidateFamily:
    """Build Gamma(X)=A_max(X) from the finite observation index universe."""
    return observation_candidate_family(observation)


def select_stage2d_partition(
    observation: Observation3D,
    energy: Stage2DEnergy,
    unit_builder: Callable[[Tuple[int, ...]], StructuralUnit] | None = None,
) -> Partition:
    """Select an energy minimizer over observation-derived Gamma(X)."""
    if energy.observation != observation:
        raise ValueError("Stage 2D energy must be defined on the supplied observation")
    family = build_gamma(observation.points)
    partitions = family.materialize() if unit_builder is None else family.materialize(unit_builder)
    if not partitions:
        raise ValueError("Observation-derived Gamma(X) must be non-empty")
    return min(partitions, key=lambda partition: evaluate_energy(partition, energy))


def run_observation_derived_pipeline(
    points: Sequence[Tuple[float, float, float]],
    separation_margin: float = 0.0,
) -> TheoryPipelineResult:
    """Run X -> A_max/Gamma -> E_2D -> Unit -> C_R -> Relation -> World -> Phi_X."""
    context = ObservationDerivedContext.from_points(points)
    energy = Stage2DEnergy.from_observation(
        context,
        lambda_complexity=1.0,
        lambda_boundary=1.0,
        separation_margin=separation_margin,
    )
    partitions = context.materialize_partitions()
    if separation_margin > 0.0:
        energy.require_separation_margin(partitions, separation_margin)
    selection = select_stable_partition(partitions, StructuralEnergy(energy))
    partition = selection.partition
    relations = form_observation_relations(partition.units, context)
    world = StructuralWorld(units=partition.units, relations=relations.relations, attributes={})
    return TheoryPipelineResult(
        partition_selection=selection,
        world=world,
        canonical=canonical_form(world),
        representation=phi_x(world, context),
    )


__all__ = [
    "TheoryPipelineResult",
    "run_theory_pipeline",
    "run_observation_derived_pipeline",
    "build_gamma",
    "select_stage2d_partition",
]
