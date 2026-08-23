"""Canonical observation-only Struct3D pipeline.

This module is the release-facing bridge for the final Hypothesis Elimination.
It makes the former theorem boundaries explicit functions of one finite
observation X:

    X -> A_max(X), Gamma(X), M(X), G_B(X), N_X, S_X, C_R(X), Phi_X
      -> Stage 2D -> Unit -> Relation -> World -> Representation.

The low-level explicit-input APIs remain available for regression and generic
mathematical use, but this pipeline is the canonical theory-facing entry point.
No semantic labels and no neural network are used.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Tuple

from .theory_core import Partition, StructuralUnit, select_minimizer
from .theory_energy_model import Observation3D, Stage2DEnergy
from .theory_observation import ObservationDerivedContext
from .theory_representation import StructuralRepresentation
from .theory_relation_formation import form_observation_relations
from .theory_world import StructuralWorld

Point = Tuple[float, float, float]


@dataclass(frozen=True)
class ObservationRepresentationMap:
    """The observation-derived coordinate map Phi_X: W_X -> R^23."""

    context: ObservationDerivedContext

    def __call__(self, world: StructuralWorld) -> StructuralRepresentation:
        return self.context.phi_x(world)


@dataclass(frozen=True)
class ObservationDerivedPipeline:
    """Single provenance carrier for the closed X -> World -> Phi_X path."""

    context: ObservationDerivedContext

    @classmethod
    def from_points(cls, points: Sequence[Point]) -> "ObservationDerivedPipeline":
        return cls(ObservationDerivedContext.from_points(points))

    @property
    def X(self) -> Observation3D:
        return self.context.observation

    # Former external boundaries, now all deterministic projections of X.
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
    def C_R(self):
        return self.context.relation_candidates(len(self.unit_family))

    @property
    def unit_family(self) -> Tuple[StructuralUnit, ...]:
        return self.context.unit_candidates

    @property
    def Phi_X(self) -> ObservationRepresentationMap:
        return ObservationRepresentationMap(self.context)

    def N_X(self, unit: StructuralUnit):
        return self.context.neighborhood_rule(unit)

    def S_X(self, unit: StructuralUnit):
        return self.context.proper_subcandidates(unit)

    @property
    def energy(self) -> Stage2DEnergy:
        return self.context.stage2d_energy()

    @property
    def partitions(self) -> Tuple[Partition, ...]:
        return self.context.materialize_partitions()

    def select_partition(self) -> Partition:
        """Select the Stage-2D argmin over the observation-derived Gamma(X)."""
        return select_minimizer(self.partitions, self.energy)

    def world(self) -> StructuralWorld:
        """Construct W=(U,R,Phi) without an externally supplied partition."""
        partition = self.select_partition()
        relations = form_observation_relations(partition.units, self.context)
        return StructuralWorld(
            units=partition.units,
            relations=relations.relations,
            attributes={},
            observation_context=self.context,
        )

    def representation(self) -> StructuralRepresentation:
        """Evaluate the observation-derived Phi_X on the derived World."""
        return self.Phi_X(self.world())

    def derived_margin(self) -> float:
        """Return the quotient-distinct Stage-2D energy margin delta_X."""
        return self.energy.derived_separation_margin(self.partitions)

    def audit(self) -> dict:
        """Return machine-checkable closure facts for the six former boundaries."""
        world = self.world()
        representation = self.Phi_X(world)
        return {
            "A_max_nonempty": bool(self.A_max),
            "A_max_finite": len(self.A_max) < float("inf"),
            "Gamma_equals_A_max": set(self.Gamma) == set(self.A_max),
            "M_finite": bool(self.M),
            "G_B_finite": len(self.G_B.edges) < float("inf"),
            "N_X_finite": all(len(self.N_X(u).candidates) < float("inf") for u in self.unit_family),
            "S_X_finite": all(len(self.S_X(u)) < float("inf") for u in self.unit_family),
            "C_R_finite": len(self.C_R) < float("inf"),
            "World_derived_from_X": world.observation_context is self.context,
            "Phi_X_dimension": len(representation.values),
        }


__all__ = ["ObservationRepresentationMap", "ObservationDerivedPipeline"]
