"""Structural invariant layer.

Frozen quotient chain:
    W -> C_Q(W) -> I(W) -> Phi([W]).

The quotient representative C_Q is index-free and therefore compatible with
observation/unit relabeling.  Raw support indices are not allowed to enter the
frozen invariant used by the representation layer.
"""

from __future__ import annotations

from typing import Any

from .theory_world import StructuralWorld
from .theory_world_quotient import world_quotient_form


def structural_invariant(world: StructuralWorld) -> Any:
    """Return the exact index-free structural invariant I(W)=C_Q(W)."""
    return world_quotient_form(world)


def invariant_equal(a: StructuralWorld, b: StructuralWorld) -> bool:
    """Test equality of the frozen Structural World quotient invariant."""
    return structural_invariant(a) == structural_invariant(b)
