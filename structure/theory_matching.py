"""Theory-facing Structural Matching interface.

Matching is defined as minimization of an explicitly supplied cost over an
explicit admissible set. The implementation therefore does not invent a
correspondence or claim uniqueness when several candidates tie.
"""

from __future__ import annotations

import math
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

    scored = []
    for candidate in candidates:
        value = float(cost(candidate))
        if not math.isfinite(value):
            raise ValueError("matching cost must be finite")
        scored.append((tuple(candidate), value))

    # Python's min is stable, so an exact tie is deterministic without being
    # interpreted as evidence of a unique optimum.
    pairs, value = min(scored, key=lambda item: item[1])
    return Match(pairs, value)
