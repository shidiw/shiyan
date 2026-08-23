"""Frozen formal interface for the observation-derived Struct3D theory.

This interface is the theorem boundary for the hypothesis-eliminated path.
Every object below is a function of one finite observation X.  The interface
contains no caller-supplied A(X), M(X), G_B(X), N_X/S_X, C_R(X), or Phi_X.

The concrete implementation is :class:`ObservationDerivedBoundaries` in
``theory_closed_form.py``.  Low-level explicit-input APIs remain available for
compatibility, but theorem-facing code should depend on this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Sequence, Tuple

from .theory_core import StructuralUnit
from .theory_observation import Point


class ObservationDerivedTheoryInterface(ABC):
    """Frozen X-derived interface for the complete upstream provenance chain.

    Mathematical dependency:

        X -> A_max/Gamma -> M, G_B, N_X/S_X -> E -> Unit
          -> C_R -> Relation/World -> Phi_X.

    The interface intentionally exposes derived objects as read-only
    properties/methods.  There is no setter or constructor argument through
    which an external theorem hypothesis can replace one of these objects.
    """

    @classmethod
    @abstractmethod
    def from_points(cls, points: Sequence[Point]):
        """Construct the complete theory boundary from observation X alone."""
        raise NotImplementedError

    @property
    @abstractmethod
    def X(self) -> Any:
        raise NotImplementedError

    @property
    @abstractmethod
    def A_max(self) -> Any:
        """A_max(X) = complete finite partition family Pi(Omega_X)."""
        raise NotImplementedError

    @property
    @abstractmethod
    def Gamma(self) -> Any:
        """Gamma(X), the frozen computational candidate family."""
        raise NotImplementedError

    @property
    @abstractmethod
    def M(self) -> Any:
        """M(X), the finite observation-derived model family."""
        raise NotImplementedError

    @property
    @abstractmethod
    def G_B(self) -> Any:
        """G_B(X), the observation-derived boundary graph."""
        raise NotImplementedError

    @property
    @abstractmethod
    def units(self) -> Tuple[StructuralUnit, ...]:
        """X-derived Unit family after the frozen formation path."""
        raise NotImplementedError

    @abstractmethod
    def N_X(self, unit: StructuralUnit) -> Any:
        """N_X(unit), the finite observation-derived stability neighborhood."""
        raise NotImplementedError

    @abstractmethod
    def S_X(self, unit: StructuralUnit) -> Any:
        """S_X(unit), the finite observation-derived proper-subcandidate family."""
        raise NotImplementedError

    @property
    @abstractmethod
    def C_R(self) -> Any:
        """C_R(X), the finite candidate relation-pair domain."""
        raise NotImplementedError

    @property
    @abstractmethod
    def Phi_X(self) -> Any:
        """Phi_X, the frozen observation-derived representation map."""
        raise NotImplementedError

    @property
    @abstractmethod
    def energy(self) -> Any:
        """Stage 2D E_X bound to the same observation provenance carrier."""
        raise NotImplementedError

    @abstractmethod
    def world(self) -> Any:
        """Build W only from the X-derived Unit/Relation chain."""
        raise NotImplementedError

    @abstractmethod
    def representation(self) -> Any:
        """Evaluate Phi_X on the X-derived World."""
        raise NotImplementedError

    @abstractmethod
    def is_closed(self) -> bool:
        """Validate the observation-provenance closure invariants."""
        raise NotImplementedError


__all__ = ["ObservationDerivedTheoryInterface"]
