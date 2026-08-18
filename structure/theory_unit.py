"""Theory-facing Structural Unit.

A structural unit is the atomic vertex object used by the frozen theory-facing
World/Relation/Graph layer. This module intentionally contains no primitive
discovery heuristic or energy calculation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Tuple


@dataclass(frozen=True)
class StructuralUnit:
    """Finite structural unit with explicit support and primitive label."""

    indices: Tuple[int, ...]
    primitive: str
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.indices:
            raise ValueError("structural unit cannot be empty")
        normalized = tuple(int(i) for i in self.indices)
        if any(i < 0 for i in normalized):
            raise ValueError("unit indices must be nonnegative")
        if len(set(normalized)) != len(normalized):
            raise ValueError("unit indices must be distinct")
        if not isinstance(self.primitive, str) or not self.primitive:
            raise ValueError("unit primitive must be a non-empty string")
        object.__setattr__(self, "indices", normalized)
        object.__setattr__(self, "attributes", dict(self.attributes))
