"""End-to-end theory-facing Struct3D pipeline.

The pipeline composes the frozen mathematical interfaces without importing
legacy heuristics. Discovery of candidate units, observation-derived theta,
energy, relation evidence, and v4.0 feature extraction are explicit theory
interfaces.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence, Tuple

from .theory_canonical import canonical_form
from .theory_candidates import ObservationCandidateFamily, observation_candidate_family
from .theory_core import Partition, TheoryUnit, evaluate_energy, StructuralUnit
from .theory_energy import StructuralEnergy
from .theory_energy_model import Observation3D, Stage2DEnergy
from .theory_observation_theta import observation_unit
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


def observation_unit_builder(observation: Observation3D) -> Callable[[Tuple[int, ...]], StructuralUnit]:
    """Return the frozen observation-derived builder A -> (A,T_X(A))."""
    return lambda indices: observation_unit(observation, indices)


def select_stage2d_partition(
    observation: Observation3D,
    energy: Stage2DEnergy,
) -> Partition:
    """Select argmin over Gamma(X), with theta=T_X(A) on every Unit.

    The closed upstream chain is now:
        X -> Gamma(X) -> P* = argmin E_2D -> U_A=(A,T_X(A)).
    """
    if energy.observation != observation:
        raise ValueError("Stage 2D energy must be defined on the supplied observation")
    family = build_gamma(observation.points)
    partitions = family.materialize(observation_unit_builder(observation))
    if not partitions:
        raise ValueError("Observation-derived Gamma(X) must be non-empty")
    return min(partitions, key=lambda partition: evaluate_energy(partition, energy))


__all__ = [
    "TheoryPipelineResult",
    "run_theory_pipeline",
    "build_gamma",
    "observation_unit_builder",
    "select_stage2d_partition",
]
