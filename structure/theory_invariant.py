"""Structural invariant layer.

The frozen chain is
    W -> C(W) -> I(W) -> phi(W).

For the current finite theory, the canonical form C(W) is itself the exact
label-invariant structural object. Therefore I(W) is defined as C(W) rather
than introducing a second, unproved numerical statistic.
"""

from __future__ import annotations

from typing import Any

from .theory_canonical import canonical_form
from .theory_world import StructuralWorld


def structural_invariant(world: StructuralWorld) -> Any:
    """Return the exact label-invariant structural object I(W)=C(W)."""
    return canonical_form(world)


def invariant_equal(a: StructuralWorld, b: StructuralWorld) -> bool:
    """Test equality of the frozen structural invariant."""
    return structural_invariant(a) == structural_invariant(b)
