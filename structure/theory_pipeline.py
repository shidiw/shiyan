"""End-to-end theory-facing Struct3D pipeline.

The pipeline composes the frozen mathematical interfaces without importing
legacy heuristics. Discovery of candidate units, energy, relation evidence,
and v4.0 feature extraction are explicit inputs.
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
from .theory_representation import StructuralRepresentation, represent
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
    world = StructuralWorld(
        units=partition.units,
        relations=tuple(relations),
        attributes={},
    )
    return TheoryPipelineResult(
        partition_selection=selection,
        world=world,
        canonical=canonical_form(world),
        representation=represent(world, representation_extractor),
    )


def build_gamma(observation: Sequence[object]) -> ObservationCandidateFamily:
    """Build the frozen Gamma(X)=A_max(X) family from observation indices only."""
    return observation_candidate_family(observation)


def select_stage2d_partition(
    observation: Observation3D,
    energy: Stage2DEnergy,
    unit_builder: Callable[[Tuple[int, ...]], StructuralUnit] | None = None,
) -> Partition:
    """Select an energy minimizer over the observation-derived Gamma(X).

    This closes the upstream chain:
        X -> Gamma(X) -> argmin_{P in Gamma(X)} E_2D(P).
    """
    if energy.observation != observation:
        raise ValueError("Stage 2D energy must be defined on the supplied observation")
    family = build_gamma(observation.points)
    partitions = family.materialize() if unit_builder is None else family.materialize(unit_builder)
    if not partitions:
        raise ValueError("Observation-derived Gamma(X) must be non-empty")
    return min(partitions, key=lambda partition: evaluate_energy(partition, energy))


__all__ = [
    "TheoryPipelineResult",
    "run_theory_pipeline",
    "build_gamma",
    "select_stage2d_partition",
]
