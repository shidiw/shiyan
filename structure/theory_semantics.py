"""Finite, non-neural semantic encoding for Struct3D Units.

Frozen Unit definition:
    u = (G, theta)

The semantic encoder Psi_U is deliberately finite and symbolic.  It is not a
learned representation and it does not depend on a geometric model family.

Admissible theta values are finite typed trees built from:
    None, bool, int, finite float, str,
    finite tuple/list, and finite mappings with string keys.

Every node is encoded together with its type tag and mappings are sorted by
key.  Consequently the encoder is injective on this frozen finite domain.

The semantic discrepancy is the discrete metric
    d_sem(a,b) = 0 iff Psi_U(a)=Psi_U(b), else 1.

For a finite candidate set containing at least two distinct theta values, the
smallest positive semantic distance is therefore exactly 1.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any, Tuple


EncodedTheta = Tuple[Any, ...]


def _encode(value: Any) -> Any:
    """Return a canonical typed encoding of one admissible theta value."""
    if value is None:
        return ("none",)
    if isinstance(value, bool):
        return ("bool", value)
    if isinstance(value, int) and not isinstance(value, bool):
        return ("int", value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("theta floats must be finite")
        return ("float", value)
    if isinstance(value, str):
        return ("str", value)
    if isinstance(value, tuple):
        return ("tuple", tuple(_encode(item) for item in value))
    if isinstance(value, list):
        return ("list", tuple(_encode(item) for item in value))
    if isinstance(value, Mapping):
        encoded_items = []
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("theta mapping keys must be strings")
            encoded_items.append((key, _encode(item)))
        encoded_items.sort(key=lambda pair: pair[0])
        return ("mapping", tuple(encoded_items))
    raise TypeError(
        "theta contains an unsupported value type; admissible values are "
        "None, bool, int, finite float, str, tuple/list, and string-keyed mappings"
    )


def psi_u(theta: Mapping[str, Any]) -> EncodedTheta:
    """Return the strictly injective semantic encoding Psi_U(theta)."""
    if not isinstance(theta, Mapping):
        raise TypeError("theta must be a mapping")
    return _encode(dict(theta))


def psi_u_injective(a: Mapping[str, Any], b: Mapping[str, Any]) -> bool:
    """Executable injectivity witness for a pair of admissible attributes."""
    encoded_equal = psi_u(a) == psi_u(b)
    return encoded_equal == (dict(a) == dict(b))


def semantic_distance(a: Mapping[str, Any], b: Mapping[str, Any]) -> float:
    """Return the discrete semantic metric induced by Psi_U."""
    return 0.0 if psi_u(a) == psi_u(b) else 1.0


def unit_equivalent(
    support_a: Tuple[int, ...],
    theta_a: Mapping[str, Any],
    support_b: Tuple[int, ...],
    theta_b: Mapping[str, Any],
) -> bool:
    """Return the frozen Structural Unit equivalence relation."""
    return tuple(support_a) == tuple(support_b) and psi_u(theta_a) == psi_u(theta_b)


__all__ = ["psi_u", "psi_u_injective", "semantic_distance", "unit_equivalent"]
