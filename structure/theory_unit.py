"""Theory-facing Structural Unit.

Frozen mathematical definition:
    u_i = (G_i, theta_i)

``indices`` encode the finite support G_i and ``attributes`` encode theta_i.
The optional primitive field is historical metadata only; it is not part of
unit identity.

The theory-facing API uses ``StructuralUnit(indices, attributes, primitive)``.
For compatibility with the pre-refactor tests and legacy engineering code,
``StructuralUnit(indices, primitive, attributes)`` is also accepted when the
second argument is a string and the third argument is a mapping.  Both forms
materialize to the same mathematical object (G, theta) plus optional metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Tuple


@dataclass(frozen=True, init=False)
class StructuralUnit:
    indices: Tuple[int, ...]
    attributes: Mapping[str, Any] = field(default_factory=dict)
    primitive: Optional[str] = None

    def __init__(self, indices: Tuple[int, ...], attributes=None, primitive=None):
        """Construct the single theory-level Unit type.

        Canonical form::

            StructuralUnit(indices, attributes, primitive=None)

        Legacy compatibility form::

            StructuralUnit(indices, primitive, attributes)

        The compatibility branch is intentionally limited to the unambiguous
        ``(str, Mapping)`` pattern so legacy callers cannot silently redefine
        the mathematical meaning of ``(G, theta)``.
        """
        if isinstance(attributes, str) and isinstance(primitive, Mapping):
            attributes, primitive = primitive, attributes

        if attributes is None:
            attributes = {}
        if not isinstance(attributes, Mapping):
            raise ValueError("unit attributes must be a mapping or None")
        if primitive is not None and not isinstance(primitive, str):
            raise ValueError("primitive metadata must be a string or None")

        object.__setattr__(self, "indices", tuple(indices))
        object.__setattr__(self, "attributes", dict(attributes))
        object.__setattr__(self, "primitive", primitive)
        self.__post_init__()

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
