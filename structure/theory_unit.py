"""Theory-facing Structural Unit.

Frozen mathematical definition:
    u_i = (G_i, theta_i)

``indices`` encode the finite support G_i and ``attributes`` encode theta_i.
The optional primitive field is historical metadata only; it is not part of
unit identity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Tuple


@dataclass(frozen=True)
class StructuralUnit:
    indices: Tuple[int, ...]
    attributes: Mapping[str, Any] = field(default_factory=dict)
    primitive: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.indices:
            raise ValueError("structural unit cannot be empty")
        normalized = tuple(int(i) for i in self.indices)
        if any(i < 0 for i in normalized):
            raise ValueError("unit indices must be nonnegative")
        if tuple(sorted(set(normalized))) != normalized:
            raise ValueError("unit indices must be unique and sorted")
        if self.attributes is None:
            raise ValueError("unit attributes cannot be None")
        if self.primitive is not None and not isinstance(self.primitive, str):
            raise ValueError("primitive metadata must be a string or None")
        object.__setattr__(self, "indices", normalized)
        object.__setattr__(self, "attributes", dict(self.attributes))

    @property
    def support(self) -> Tuple[int, ...]:
        return self.indices

    @property
    def theta(self) -> Mapping[str, Any]:
        return self.attributes


__all__ = ["StructuralUnit"]
