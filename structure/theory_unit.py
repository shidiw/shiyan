"""Theory-facing Structural Unit.

Frozen mathematical definition:
    u_i = (G_i, theta_i)

For a finite point-cloud implementation, ``indices`` are the discrete support
encoding of G_i and ``attributes`` are theta_i. A primitive label is optional
metadata: the theory explicitly distinguishes a Structural Unit from a
Primitive, so primitive information must never be required for Unit identity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Tuple


@dataclass(frozen=True)
class StructuralUnit:
    """Finite implementation of a structural unit u=(G, theta)."""

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
        if self.primitive is not None and (
            not isinstance(self.primitive, str) or not self.primitive
        ):
            raise ValueError("primitive metadata must be a non-empty string or None")
        object.__setattr__(self, "indices", normalized)
        object.__setattr__(self, "attributes", dict(self.attributes))

    @property
    def support(self) -> Tuple[int, ...]:
        """Discrete support G of the mathematical unit u=(G, theta)."""
        return self.indices

    @property
    def theta(self) -> Mapping[str, Any]:
        """Structural attributes theta of the mathematical unit."""
        return self.attributes
