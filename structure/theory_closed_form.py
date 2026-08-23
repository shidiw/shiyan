"""Strict observation-derived boundary bundle for the Struct3D theory.

This module is the release-facing Hypothesis Elimination facade. It exposes
only objects generated from one finite observation X; callers cannot inject
A(X), M(X), G_B(X), N_X/S_X, C_R(X), or Phi_X as independent theorem inputs.

The concrete bundle now implements the frozen formal interface in
``theory_observation_interface.py``. Low-level compatibility APIs remain
available, but this class is the release-facing theorem boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Tuple

from .theory_observation import ObservationDerivedContext, Point
from .theory_observation_pipeline import ObservationDerivedPipeline, ObservationRepresentationMap
from .theory_observation_interface import ObservationDerivedTheoryInterface
from .theory_core import StructuralUnit


@dataclass(frozen=True)
class ObservationDerivedBoundaries(ObservationDerivedTheoryInterface):
    """All formerly external theory boundaries generated from one X.

    The two stored fields are themselves immutable provenance carriers built
    from the same observation. No mathematical boundary is accepted as an
    independent constructor argument.
    """

    context: ObservationDerivedContext
    pipeline: ObservationDerivedPipeline

    @classmethod
    def from_points(cls, points: Sequence[Point]) -> "ObservationDerivedBoundaries":
        pipeline = ObservationDerivedPipeline.from_points(points)
        return cls(pipeline.context, pipeline)

    @property
    def X(self):
        return self.context.observation

    @property
    def A_max(self):
        return self.context.a_max

    @property
    def Gamma(self):
        return self.context.gamma

    @property
    def M(self):
        return self.context.model_family

    @property
    def G_B(self):
        return self.context.boundary_graph

    @property
    def units(self) -> Tuple[StructuralUnit, ...]:
        return self.context.unit_candidates

    def N_X(self, unit: StructuralUnit):
        return self.context.neighborhood_rule(unit)

    def S_X(self, unit: StructuralUnit):
        return self.context.proper_subcandidates(unit)

    @property
    def C_R(self):
        """C_R(X): ordered candidate pairs over X-derived selected Units."""
        selected = self.pipeline.selected_units
        return tuple((i, j) for i in range(len(selected)) for j in range(len(selected)) if i != j)

    @property
    def Phi_X(self) -> ObservationRepresentationMap:
        return self.pipeline.Phi_X

    @property
    def energy(self):
        return self.context.stage2d_energy()

    def world(self):
        return self.pipeline.world()

    def representation(self):
        return self.Phi_X(self.world())

    def is_closed(self) -> bool:
        """Check the structural provenance invariants of the closed path."""
        world = self.world()
        representation = self.representation()
        return (
            bool(self.A_max)
            and bool(self.Gamma)
            and set(self.Gamma).issubset(set(self.A_max))
            and bool(self.M)
            and self.G_B.universe_size == len(self.X.points)
            and all(self.N_X(unit) is not None for unit in self.units)
            and all(self.S_X(unit) is not None for unit in self.units)
            and len(self.C_R) == len(world.units) * (len(world.units) - 1)
            and world.observation_context is self.context
            and len(representation.values) == 23
        )


__all__ = ["ObservationDerivedBoundaries"]
