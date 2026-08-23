"""Interface-consistency theorem for the observation-derived Struct3D path.

For one valid finite observation X, every canonical theorem object must be
provably sourced from that same X.  This module is an executable theorem
contract: it checks provenance, finiteness, domain agreement, and the final
World -> Phi_X map without accepting any independent theorem boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class InterfaceConsistencyResult:
    """Executable witness for the X-only interface consistency theorem."""

    observation_valid: bool
    a_max_finite_nonempty: bool
    gamma_subset_a_max: bool
    model_bound_to_x: bool
    boundary_bound_to_x: bool
    energy_bound_to_x: bool
    world_bound_to_x: bool
    representation_bound_to_x: bool
    representation_dimension: int
    closed: bool


def prove_observation_interface_consistency(boundaries) -> InterfaceConsistencyResult:
    """Check that the release-facing theorem interface has one X provenance.

    The theorem boundary is the immutable ``ObservationDerivedBoundaries``
    object.  No A/M/G_B/N/S/C_R/Phi object is accepted as an argument here.
    """
    x = boundaries.X
    context = boundaries.context

    observation_valid = bool(x.points) and all(
        len(point) == 3 and all(isfinite(float(v)) for v in point)
        for point in x.points
    )

    a_max = boundaries.A_max
    gamma = boundaries.Gamma
    a_max_ok = bool(a_max) and len(a_max) < float("inf")
    gamma_ok = bool(gamma) and set(gamma).issubset(set(a_max))

    model_bound = boundaries.context.models.observation == x
    boundary_bound = boundaries.context.boundary.observation == x
    energy_bound = boundaries.energy.observation == x and boundaries.energy.observation_context is context

    world = boundaries.world()
    world_bound = world.observation_context is context and world.observation_context.observation == x

    representation = boundaries.Phi_X(world)
    representation_bound = boundaries.Phi_X.context.observation == x
    dimension = len(representation.values)

    closed = (
        observation_valid
        and a_max_ok
        and gamma_ok
        and model_bound
        and boundary_bound
        and energy_bound
        and world_bound
        and representation_bound
        and dimension == 23
    )

    return InterfaceConsistencyResult(
        observation_valid=observation_valid,
        a_max_finite_nonempty=a_max_ok,
        gamma_subset_a_max=gamma_ok,
        model_bound_to_x=model_bound,
        boundary_bound_to_x=boundary_bound,
        energy_bound_to_x=energy_bound,
        world_bound_to_x=world_bound,
        representation_bound_to_x=representation_bound,
        representation_dimension=dimension,
        closed=closed,
    )


__all__ = ["InterfaceConsistencyResult", "prove_observation_interface_consistency"]
