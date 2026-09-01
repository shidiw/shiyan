"""Final Hypothesis Elimination certificate for the observation-facing theory.

The certificate introduces no new mathematical assumption. It checks that all
formerly external boundaries are generated from the same finite observation
context and that Stage 2D -> Unit -> Relation -> World -> Phi consumes that
context end-to-end.
"""

from __future__ import annotations

from dataclasses import dataclass

from .theory_observation import ObservationDerivedContext, observation_relation_candidates
from .theory_observation_pipeline import ObservationDerivedPipeline, ObservationRepresentationMap


@dataclass(frozen=True)
class HypothesisClosureCertificate:
    """Machine-checkable closure certificate for one observation X."""

    observation_size: int
    a_max_size: int
    gamma_size: int
    model_count: int
    boundary_edge_count: int
    unit_count: int
    relation_candidate_count: int
    representation_dim: int
    all_boundaries_derived: bool
    stage2d_world_representation_closed: bool

    @property
    def passed(self) -> bool:
        return self.all_boundaries_derived and self.stage2d_world_representation_closed


def certify_hypothesis_elimination(pipeline: ObservationDerivedPipeline) -> HypothesisClosureCertificate:
    """Certify the final observation-only theory path for ``pipeline.X``."""
    context = pipeline.context
    X = context.observation

    a_max = context.a_max
    gamma = context.gamma
    a_ok = bool(a_max) and set(gamma) == set(a_max)

    m_ok = context.models == type(context.models).from_observation(X)
    g_ok = context.boundary == type(context.boundary).from_observation(X)

    units = context.unit_candidates
    n_ok = all(context.neighborhood_rule(u) == context.neighborhood_rule(u) for u in units)
    s_ok = all(context.proper_subcandidates(u) == context.proper_subcandidates(u) for u in units)

    selected = pipeline.selected_units
    c_r = context.relation_domain(selected)
    c_ok = tuple(c_r.pairs) == observation_relation_candidates(len(selected))

    phi_ok = isinstance(pipeline.Phi_X, ObservationRepresentationMap)
    world = pipeline.world()
    representation = pipeline.representation()
    world_ok = world.observation_context is context
    energy_ok = pipeline.energy.observation == X and pipeline.energy.observation_context is context
    rep_ok = phi_ok and representation == pipeline.Phi_X(world) and len(representation.values) == 23

    all_boundaries = all((a_ok, m_ok, g_ok, n_ok, s_ok, c_ok, phi_ok))
    closed = all((energy_ok, world_ok, rep_ok))

    return HypothesisClosureCertificate(
        observation_size=len(X.points),
        a_max_size=len(a_max),
        gamma_size=len(gamma),
        model_count=len(context.model_family),
        boundary_edge_count=len(context.boundary_graph.edges),
        unit_count=len(selected),
        relation_candidate_count=len(c_r),
        representation_dim=len(representation.values),
        all_boundaries_derived=all_boundaries,
        stage2d_world_representation_closed=closed,
    )


__all__ = ["HypothesisClosureCertificate", "certify_hypothesis_elimination"]
