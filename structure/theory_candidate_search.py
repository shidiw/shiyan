"""Observation-derived scalable candidate generator.

A_max(X) is the complete finite partition lattice and remains the mathematical
admissible universe.  Gamma(X) is the frozen *computational* finite subfamily
used by the theory-facing pipeline.  A_search(X) is retained only as a
backward-compatible scalability approximation and is never the provenance
source of the main pipeline.

Gamma(X) is deterministic, label-free, finite, non-empty, and quotient
compatible. Its default strategies are the whole partition, singleton
partition, and deterministic farthest-pair Voronoi bipartition.
"""

from __future__ import annotations

from itertools import combinations
from typing import Iterable, Sequence, Tuple

from .theory_candidates import PartitionBlocks, partition_from_blocks
from .theory_energy_model import Observation3D


def _canonical(blocks: Iterable[Iterable[int]]) -> PartitionBlocks:
    return tuple(sorted((tuple(sorted(block)) for block in blocks if block), key=lambda b: (b[0], len(b), b)))


def _whole(n: int) -> PartitionBlocks:
    return (tuple(range(n)),)


def _singletons(n: int) -> PartitionBlocks:
    return tuple((i,) for i in range(n))


def _farthest_pair(points: Tuple[Tuple[float, float, float], ...]) -> Tuple[int, int]:
    best = None
    best_key = None
    for i, j in combinations(range(len(points)), 2):
        distance2 = sum((points[i][k] - points[j][k]) ** 2 for k in range(3))
        coordinate_key = (tuple(points[i]), tuple(points[j]), i, j)
        key = (distance2, coordinate_key)
        if best_key is None or key > best_key:
            best_key = key
            best = (i, j)
    if best is None:
        raise ValueError("At least two points are required for a bipartition")
    return best


def _farthest_split(observation: Observation3D) -> PartitionBlocks:
    points = observation.points
    left_seed, right_seed = _farthest_pair(points)
    left = []
    right = []
    for index, point in enumerate(points):
        dl = sum((point[k] - points[left_seed][k]) ** 2 for k in range(3))
        dr = sum((point[k] - points[right_seed][k]) ** 2 for k in range(3))
        if dl < dr or (dl == dr and left_seed < right_seed):
            left.append(index)
        else:
            right.append(index)
    if not left or not right:
        return _singletons(len(points))
    return _canonical((left, right))


def Gamma_X(
    observation: Observation3D,
    strategies: Sequence[str] = ("whole", "singletons", "farthest_split"),
) -> Tuple[PartitionBlocks, ...]:
    """Construct the frozen finite computational family Gamma(X) subset A_max(X)."""
    n = len(observation.points)
    if n <= 0:
        raise ValueError("Observation must be non-empty")

    registry = {
        "whole": lambda: _whole(n),
        "singletons": lambda: _singletons(n),
        "farthest_split": lambda: _farthest_split(observation) if n > 1 else _whole(n),
    }
    blocks = []
    for strategy in strategies:
        if strategy not in registry:
            raise ValueError(f"Unknown Gamma strategy: {strategy}")
        blocks.append(registry[strategy]())

    unique = tuple(dict.fromkeys(blocks))
    for candidate in unique:
        partition_from_blocks(candidate)
    return unique


def materialize_Gamma(
    observation: Observation3D,
    strategies: Sequence[str] = ("whole", "singletons", "farthest_split"),
):
    return tuple(partition_from_blocks(blocks) for blocks in Gamma_X(observation, strategies))


def A_search(
    observation: Observation3D,
    strategies: Sequence[str] = ("whole", "singletons", "farthest_split"),
) -> Tuple[PartitionBlocks, ...]:
    """Deprecated compatibility wrapper; A_search is only a scalability approximation."""
    return Gamma_X(observation, strategies)


def materialize_A_search(
    observation: Observation3D,
    strategies: Sequence[str] = ("whole", "singletons", "farthest_split"),
):
    """Deprecated compatibility wrapper for the scalability approximation."""
    return materialize_Gamma(observation, strategies)


def is_subset_of_A_max(observation: Observation3D, candidates: Sequence[PartitionBlocks]) -> bool:
    from .theory_candidates import maximal_admissible_partitions
    # This exact subset check is intended only for small regression observations;
    # the main pipeline never enumerates A_max(X).
    return set(candidates).issubset(
        set(maximal_admissible_partitions(tuple(range(len(observation.points)))))
    )


__all__ = [
    "Gamma_X",
    "materialize_Gamma",
    "A_search",
    "materialize_A_search",
    "is_subset_of_A_max",
]
