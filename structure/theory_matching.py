"""Theory-facing Structural Matching interface.

The formal theory defines matching as an optimization over admissible
correspondences. The exact matching cost remains an explicit input because
the historical document does not freeze a unique final cost decomposition.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence, Tuple


@dataclass(frozen=True)
class Match:
    pairs: Tuple[Tuple[int, int], ...]
    cost: float


def select_matching(
    candidates: Sequence[Tuple[Tuple[int, int], ...]],
    cost: Callable[[Tuple[Tuple[int, int], ...]], float],
) -> Match:
    if not candidates:
        raise ValueError("At least one admissible matching is required")
    scored = [(candidate, float(cost(candidate))) for candidate in candidates]
    pairs, value = min(scored, key=lambda item: item[1])
    if value != value:
        raise ValueError("matching cost cannot be NaN")
    return Match(tuple(pairs), value)
