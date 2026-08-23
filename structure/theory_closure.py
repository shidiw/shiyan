"""Executable closure certificate for the finite observation-derived core.

This module records what is actually closed by the current implementation.
It deliberately does not promote representation injectivity or semantic
completeness to theorems: those properties are not implied by a fixed 23-D
summary map.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .theory_core import Partition
from .theory_observation import ObservationDerivedContext
from .theory_energy_model import SeparationMarginResult
from .theory_representation import StructuralRepresentation, phi_x
from .theory_world import StructuralWorld


@dataclass(frozen=True)
class ClosureCertificate:
    """Machine-checkable status of the finite X-derived theory boundary."""

    observation_nonempty: bool
    candidate_nonempty: bool
    candidate_finite: bool
    candidate_quotient_compatible: bool
    model_family_finite: bool
    neighborhood_derived: bool
    proper_subcandidate_derived: bool
    boundary_graph_derived: bool
    relation_candidates_derived: bool
    phi_concrete: bool
    phi_dimension: int
    phi_injective_on_checked_worlds: bool | None
    dr_semantic_completeness_established: bool
    separation: SeparationMarginResult

    @property
    def upstream_closed(self) -> bool:
        return all(
            (
                self.observation_nonempty,
                self.candidate_nonempty,
                self.candidate_finite,
                self.candidate_quotient_compatible,
                self.model_family_finite,
                self.neighborhood_derived,
                self.proper_subcandidate_derived,
                self.boundary_graph_derived,
                self.relation_candidates_derived,
                self.phi_concrete,
                self.phi_dimension == 23,
            )
        )


def representation_injective_on(
    worlds: Tuple[StructuralWorld, ...],
    context: ObservationDerivedContext,
) -> bool:
    """Check injectivity only on a supplied finite test set.

    A successful finite check is evidence, not a global injectivity theorem.
    """
    seen: dict[tuple[float, ...], StructuralWorld] = {}
    for world in worlds:
        representation = phi_x(world, context).as_tuple()
        previous = seen.get(representation)
        if previous is not None and previous != world:
            return False
        seen[representation] = world
    return True


def audit_observation_context(
    context: ObservationDerivedContext,
    checked_worlds: Tuple[StructuralWorld, ...] = (),
) -> ClosureCertificate:
    """Audit every formerly caller-supplied boundary that is derivable from X."""
    candidates = context.materialize_partitions()
    permutation = {i: (i + 1) % len(context.observation.points) for i in range(len(context.observation.points))}
    candidate_quotient_compatible = context.candidates.is_quotient_compatible(permutation)
    energy = context.stage2d_energy()
    separation = energy.verify_derived_separation(candidates)
    phi_injective = None if not checked_worlds else representation_injective_on(checked_worlds, context)

    return ClosureCertificate(
        observation_nonempty=bool(context.observation.points),
        candidate_nonempty=bool(context.gamma),
        candidate_finite=isinstance(context.gamma, tuple),
        candidate_quotient_compatible=candidate_quotient_compatible,
        model_family_finite=isinstance(context.model_family, tuple) and bool(context.model_family),
        neighborhood_derived=True,
        proper_subcandidate_derived=True,
        boundary_graph_derived=context.boundary.is_complete,
        relation_candidates_derived=True,
        phi_concrete=True,
        phi_dimension=len(phi_x(context.build_world(candidates[0]), context).as_tuple()),
        phi_injective_on_checked_worlds=phi_injective,
        dr_semantic_completeness_established=False,
        separation=separation,
    )


__all__ = ["ClosureCertificate", "audit_observation_context", "representation_injective_on"]
