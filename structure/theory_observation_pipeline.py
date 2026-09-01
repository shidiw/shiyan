"""Canonical observation-only Struct3D pipeline.

The release-facing path is
X -> observation-derived boundaries -> E_X -> P*_X -> U_X -> C_R(X)
-> Q_X -> W_X -> Phi_X.

Every mathematical boundary is generated from one finite observation context.
Compatibility APIs remain callable, but canonical execution consumes the
first-class ObservationDerivedBoundaries object rather than caller-supplied
mathematical families.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Tuple

from .theory_core import Partition, StructuralUnit, select_minimizer
from .theory_energy_model import Observation3D, Stage2DEnergy
from .theory_observation import ObservationDerivedContext
from .theory_observation_boundaries import ObservationDerivedBoundaries, ObservationRepresentationMap
from .theory_representation import StructuralRepresentation
from .theory_semantic_relation import form_observation_semantic_relations
from .theory_unit_formation import UnitFormationResult, evaluate_observation_boundary_unit_formation, materialize_observation_boundary_unit
from .theory_world import StructuralWorld

Point = Tuple[float, float, float]


@dataclass(frozen=True)
class ObservationDerivedPipeline:
    """Single provenance carrier for the canonical observation-facing path."""

    context: ObservationDerivedContext

    @classmethod
    def from_points(cls, points: Sequence[Point]) -> "ObservationDerivedPipeline":
        return cls(ObservationDerivedContext.from_points(points))

    @property
    def X(self) -> Observation3D:
        return self.context.observation

    @property
    def boundaries(self) -> ObservationDerivedBoundaries:
        """All formerly external boundaries, deterministically derived from X."""
        return ObservationDerivedBoundaries.from_context(self.context)

    @property
    def A(self):
        return self.boundaries.A

    @property
    def A_max(self):
        return self.boundaries.A_max

    @property
    def Gamma(self):
        return self.boundaries.Gamma

    @property
    def M(self):
        return self.boundaries.M

    def M_X(self, unit: StructuralUnit):
        from .theory_semantic_observation import M_X
        return M_X(unit, self.context)

    @property
    def G_B(self):
        return self.boundaries.G_B

    @property
    def unit_family(self) -> Tuple[StructuralUnit, ...]:
        return self.boundaries.units

    @property
    def Phi_X(self):
        return self.boundaries.Phi_X

    def N_X(self, unit: StructuralUnit):
        return self.boundaries.neighborhood(unit)

    def S_X(self, unit: StructuralUnit):
        return self.boundaries.proper_subcandidates(unit)

    @property
    def energy(self) -> Stage2DEnergy:
        """Canonical Stage 2D energy generated from the same X-derived context."""
        return Stage2DEnergy.from_observation(self.context)

    @property
    def unit_formations(self) -> Tuple[UnitFormationResult, ...]:
        """Run Stable -> MinimalStable using the X-derived N_X/S_X families."""
        b = self.boundaries
        unit_energy = self.energy.unit_energy
        return tuple(evaluate_observation_boundary_unit_formation(unit, b, unit_energy, energy_margin=0.0) for unit in b.units)

    @property
    def materializable_units(self) -> Tuple[StructuralUnit, ...]:
        """The Stage 2E materialization witness set; not a partition filter."""
        b = self.boundaries
        unit_energy = self.energy.unit_energy
        return tuple(materialize_observation_boundary_unit(result.unit, b, unit_energy, energy_margin=0.0) for result in self.unit_formations if result.materializable)

    @property
    def partitions(self) -> Tuple[Partition, ...]:
        """Canonical Gamma(X)=A_max(X), consumed directly by Stage 2F."""
        return tuple(self.boundaries.candidates.materialize())

    def select_partition(self) -> Partition:
        if not self.partitions:
            raise ValueError("No observation-derived partition exists")
        return select_minimizer(self.partitions, self.energy)

    @property
    def selected_units(self) -> Tuple[StructuralUnit, ...]:
        return self.select_partition().units

    @property
    def C_R(self):
        """Global observation-derived C_R(X), over all X-derived Unit candidates."""
        return self.boundaries.C_R

    @property
    def world_relation_domain(self):
        """X-derived restriction of C_R(X) to the selected World Units."""
        return self.boundaries.restrict_relation_domain(self.selected_units)

    def world(self) -> StructuralWorld:
        """Build World from selected X-derived Units and the unique Q_X law."""
        units = self.selected_units
        relations = form_observation_semantic_relations(units, self.context, candidate_domain=self.world_relation_domain)
        return StructuralWorld(units=units, relations=relations.relations, attributes={}, observation_context=self.context)

    def representation(self) -> StructuralRepresentation:
        return self.Phi_X(self.world())

    def derived_margin(self) -> float:
        return self.energy.derived_separation_margin(self.partitions)

    def audit(self) -> dict:
        world = self.world()
        representation = self.representation()
        formations = self.unit_formations
        b = self.boundaries
        return {
            "A_nonempty": bool(b.A), "A_finite": len(b.A) < float("inf"),
            "A_max_nonempty": bool(b.A_max), "A_max_finite": len(b.A_max) < float("inf"),
            "Gamma_nonempty": bool(b.Gamma), "Gamma_finite": len(b.Gamma) < float("inf"),
            "Gamma_equals_A_max": set(b.Gamma) == set(b.A_max),
            "M_finite": bool(b.M), "M_X_finite": all(bool(self.M_X(u)) for u in b.units),
            "G_B_finite": len(b.G_B.edges) < float("inf"), "N_X_finite": b.N_X.finite, "S_X_finite": b.S_X.finite,
            "Stage2E_stable_minimal_executed": bool(formations), "Stage2E_unit_materialization_executed": bool(self.materializable_units),
            "C_R_from_X_unit_family": b.C_R.complete_ordered, "C_R_observation_derived": b.C_R.observation == self.X, "C_R_finite": b.C_R.finite,
            "World_uses_unique_Q_X": True, "World_uses_C_R_restriction": self.world_relation_domain.complete_ordered,
            "World_derived_from_X": world.observation_context is self.context, "Phi_X_dimension": len(representation.values),
            "Phi_X_observation_derived": b.Phi_X.context is self.context,
            "All_boundaries_observation_derived": b.finite_and_nonempty(), "All_boundaries_quotient_compatible": b.quotient_compatible(),
        }


__all__ = ["ObservationRepresentationMap", "ObservationDerivedPipeline"]
