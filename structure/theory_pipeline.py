"""End-to-end theory-facing Struct3D pipeline.

The pipeline composes the frozen mathematical interfaces without importing
legacy heuristics. Discovery of candidate units, energy, relation evidence,
and v4.0 feature extraction are explicit inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence, Tuple

from .theory_canonical import canonical_form
from .theory_core import Partition, TheoryUnit
from .theory_energy import StructuralEnergy
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
