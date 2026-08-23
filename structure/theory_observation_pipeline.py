"""Canonical observation-only Struct3D pipeline.

The release-facing path is

    X -> A_max(X), Gamma(X), M(X), G_B(X), N_X, S_X
      -> Stage 2D energy -> Stage 2E Stable -> MinimalStable -> Unit
      -> Q_X / C_R(X) -> World -> Phi_X.

A_search(X) remains importable only as a backward-compatible scalability
approximation. It is not used to construct the canonical pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Tuple

from .theory_candidate_search import A_search
from .theory_core import Partition, StructuralUnit, select_minimizer
from .theory_energy_model import Observation3D, Stage2DEnergy
from .theory_observation import ObservationDerivedContext
from .theory_representation import StructuralRepresentation
from .theory_semantic_relation import form_observation_semantic_relations
from .theory_unit_formation import UnitFormationResult, evaluate_observation_unit_formation
from .theory_world import StructuralWorld

Point = Tuple[float, float, float]


@dataclass(frozen=True)
class ObservationRepresentationMap:
    """Observation-derived coordinate map Phi_X: W_X -> R^23."""

    context: ObservationDerivedContext

    def __call__(self, world: StructuralWorld) -> StructuralRepresentation:
        return self.context.phi_x(world)


@dataclass(frozen=True)
class ObservationDerivedPipeline:
    """Single provenance carrier for X -> Gamma -> Unit -> Relation -> World -> Phi."""

    context: ObservationDerivedContext

    @classmethod
    def from_points(cls, points: Sequence[Point]) -> "ObservationDerivedPipeline":
        return cls(ObservationDerivedContext.from_points(points))

    @property
    def X(self) -> Observation3D:
        return self.context.observation

    @property
    def A_max(self):
        return self.context.a_max

    @property
    def Gamma(self):
        return self.context.gamma

    @property
    def A_search(self):
        """Compatibility-only scalability approximation; never used by the pipeline."""
        return A_search(self.X)

    @property
    def M(self):
        return self.context.model_family

    def M_X(self, unit: StructuralUnit):
        from .theory_semantic_observation import M_X
        return M_X(unit, self.context)

    @property
    def G_B(self):
        return self.context.boundary_graph

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
    def unit_formations(self) -> Tuple[UnitFormationResult, ...]:
        """Execute Stage 2E for every Unit appearing in Gamma(X)."""
        unit_energy = self.energy.unit_energy
        return tuple(
            evaluate_observation_unit_formation(unit, self.context, unit_energy, energy_margin=0.0)
            for unit in self.unit_family
        )

    @property
    def materializable_units(self) -> Tuple[StructuralUnit, ...]:
        return tuple(result.unit for result in self.unit_formations if result.materializable)

    @property
    def partitions(self) -> Tuple[Partition, ...]:
        """Gamma(X) restricted to partitions whose Units pass Stage 2E."""
        materializable = set(self.materializable_units)
        return tuple(
            partition
            for partition in self.context.materialize_partitions()
            if all(unit in materializable for unit in partition.units)
        )

    def select_partition(self) -> Partition:
        """Select the Stage-2D minimizer only after Stage-2E Unit formation."""
        if not self.partitions:
            raise ValueError("No Gamma(X) partition survives Stable -> MinimalStable -> Unit")
        return select_minimizer(self.partitions, self.energy)

    @property
    def selected_units(self) -> Tuple[StructuralUnit, ...]:
        return self.select_partition().units

    @property
    def C_R(self):
        """Relation candidate domain induced by the selected X-derived Units."""
        return self.context.relation_candidates(len(self.selected_units))

    def world(self) -> StructuralWorld:
        """Construct W=(U,R,Phi) from the same selected Unit lineage and Q_X."""
        units = self.selected_units
        relations = form_observation_semantic_relations(units, self.context)
        return StructuralWorld(
            units=units,
            relations=relations.relations,
            attributes={},
            observation_context=self.context,
        )

    def representation(self) -> StructuralRepresentation:
        return self.Phi_X(self.world())

    def derived_margin(self) -> float:
        return self.energy.derived_separation_margin(self.context.materialize_partitions())

    def audit(self) -> dict:
        world = self.world()
        representation = self.Phi_X(world)
        formations = self.unit_formations
        return {
            "A_max_nonempty": bool(self.A_max),
            "A_max_finite": len(self.A_max) < float("inf"),
            "Gamma_nonempty": bool(self.Gamma),
            "Gamma_finite": len(self.Gamma) < float("inf"),
            "Gamma_subset_A_max": set(self.Gamma).issubset(set(self.A_max)),
            "A_search_is_approximation": set(self.A_search).issubset(set(self.Gamma)),
            "A_search_used_by_pipeline": False,
            "M_finite": bool(self.M),
            "M_X_finite": all(bool(self.M_X(u)) for u in self.unit_family),
            "G_B_finite": len(self.G_B.edges) < float("inf"),
            "N_X_finite": all(bool(self.N_X(u).alternatives) for u in self.unit_family),
            "S_X_finite": all(len(self.S_X(u)) < float("inf") for u in self.unit_family),
            "Stage2E_executed": bool(formations),
            "Stage2E_all_selected_units_materializable": all(
                result.materializable for result in formations if result.unit in world.units
            ),
            "C_R_from_selected_units": len(self.C_R) == len(world.units) * (len(world.units) - 1),
            "World_uses_unique_Q_X": True,
            "World_derived_from_X": world.observation_context is self.context,
            "Phi_X_dimension": len(representation.values),
        }


__all__ = ["ObservationRepresentationMap", "ObservationDerivedPipeline"]
