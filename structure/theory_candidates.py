"""Observation-derived admissible candidates for Struct3D.

Frozen candidate-generation boundary:

    X -> A_max(X) -> Gamma(X) -> argmin E_X -> Structural Units.

For a finite observation X with index universe Omega_X={0,...,n-1},
A_max(X) is the complete finite partition lattice Pi(Omega_X).  Gamma(X)
is the observation-derived candidate family used by the theory-facing
pipeline.  The default Gamma is A_max itself; therefore it is automatically
finite, non-empty, and quotient-compatible under observation relabeling.

No semantic labels, primitive labels, neural network, distance threshold, or
legacy heuristic participates in candidate generation.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Iterable, Iterator, Mapping, Sequence, Tuple

from .theory_core import Partition, StructuralUnit

Block = Tuple[int, ...]
PartitionBlocks = Tuple[Block, ...]


def _canonical_blocks(blocks: Iterable[Iterable[int]]) -> PartitionBlocks:
    normalized = tuple(sorted((tuple(sorted(int(i) for i in block)) for block in blocks), key=lambda b: (b[0], len(b), b)))
    return normalized


def _set_partitions(indices: Tuple[int, ...]) -> Iterator[PartitionBlocks]:
    """Yield every set partition of a finite sorted index tuple exactly once."""
    if not indices:
        yield ()
        return
    first, rest = indices[0], indices[1:]
    for blocks in _set_partitions(rest):
        # Put first into each existing block.
        for position in range(len(blocks)):
            candidate = list(blocks)
            candidate[position] = tuple(sorted((first,) + candidate[position]))
            yield _canonical_blocks(candidate)
        # Or create a new singleton block.
        yield _canonical_blocks(((first,),) + blocks)


def maximal_admissible_partitions(universe: Sequence[int]) -> Tuple[PartitionBlocks, ...]:
    """Return the complete finite partition family Pi(universe)."""
    normalized = tuple(sorted(set(int(i) for i in universe)))
    if not normalized:
        raise ValueError("Observation universe must be non-empty")
    if len(normalized) != len(tuple(universe)):
        raise ValueError("Observation universe indices must be unique")
    return tuple(dict.fromkeys(_set_partitions(normalized)))


def _default_unit_builder(indices: Block) -> StructuralUnit:
    return StructuralUnit(indices=indices, attributes={})


def partition_from_blocks(
    blocks: PartitionBlocks,
    unit_builder: Callable[[Block], StructuralUnit] = _default_unit_builder,
) -> Partition:
    """Materialize a mathematical partition as the frozen StructuralUnit type."""
    if not blocks:
        raise ValueError("Partition must contain at least one non-empty block")
    units = tuple(unit_builder(block) for block in blocks)
    universe = tuple(sorted(i for block in blocks for i in block))
    return Partition(units=units, universe=universe)


def relabel_blocks(blocks: PartitionBlocks, permutation: Mapping[int, int]) -> PartitionBlocks:
    """Apply an observation-index permutation to a partition."""
    return _canonical_blocks(tuple(permutation[i] for i in block) for block in blocks)


@dataclass(frozen=True)
class ObservationCandidateFamily:
    """Finite, non-empty, quotient-compatible candidate family derived from X."""

    universe: Tuple[int, ...]
    blocks: Tuple[PartitionBlocks, ...]

    @classmethod
    def from_universe(cls, universe: Sequence[int]) -> "ObservationCandidateFamily":
        normalized = tuple(sorted(set(int(i) for i in universe)))
        maximal = maximal_admissible_partitions(normalized)
        return cls(normalized, maximal)

    @property
    def a_max(self) -> Tuple[PartitionBlocks, ...]:
        """The mathematical maximal family A_max(X)=Pi(Omega_X)."""
        return maximal_admissible_partitions(self.universe)

    @property
    def gamma(self) -> Tuple[PartitionBlocks, ...]:
        """The frozen default Gamma(X), equal to A_max(X)."""
        return self.blocks

    def materialize(
        self,
        unit_builder: Callable[[Block], StructuralUnit] = _default_unit_builder,
    ) -> Tuple[Partition, ...]:
        return tuple(partition_from_blocks(blocks, unit_builder) for blocks in self.gamma)

    def is_maximal(self) -> bool:
        return set(self.gamma) == set(self.a_max)

    def is_quotient_compatible(self, permutation: Mapping[int, int]) -> bool:
        mapped = {relabel_blocks(blocks, permutation) for blocks in self.gamma}
        return mapped == set(self.gamma)


def observation_candidate_family(observation: Sequence[object]) -> ObservationCandidateFamily:
    """Construct Gamma(X) using only the finite observation index set."""
    if not observation:
        raise ValueError("Observation must be non-empty")
    return ObservationCandidateFamily.from_universe(tuple(range(len(observation))))


__all__ = [
    "ObservationCandidateFamily",
    "maximal_admissible_partitions",
    "observation_candidate_family",
    "partition_from_blocks",
    "relabel_blocks",
]
