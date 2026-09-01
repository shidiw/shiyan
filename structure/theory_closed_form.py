"""Strict observation-derived boundary bundle for the Struct3D theory.

This is the release-facing Hypothesis Elimination facade. Every former
external boundary is generated from one finite observation X.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Tuple

from .theory_core import StructuralUnit
from .theory_observation import ObservationDerivedContext, ObservationRelationCandidateDomain, Point
from .theory_observation_pipeline import ObservationDerivedPipeline, ObservationRepresentationMap
from .theory_observation_interface import ObservationDerivedTheoryInterface


@dataclass(frozen=True)
class ObservationDerivedBoundaries(ObservationDerivedTheoryInterface):
    """All formerly external boundaries generated from one X."""

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
    def C_R(self) -> ObservationRelationCandidateDomain:
        """Global C_R(X): all ordered pairs of X-derived Unit candidates."""
        return self.context.relation_domain(self.units)

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
            and set(self.Gamma) == set(self.A_max)
            and bool(self.M)
            and self.G_B.universe_size == len(self.X.points)
            and all(self.N_X(unit) is not None for unit in self.units)
            and all(self.S_X(unit) is not None for unit in self.units)
            and self.C_R.complete_ordered
            and self.C_R.observation == self.X
            and self.C_R.units == self.units
            and world.observation_context is self.context
            and len(representation.values) == 23
            and self.Phi_X.context is self.context
        )


__all__ = ["ObservationDerivedBoundaries"]
