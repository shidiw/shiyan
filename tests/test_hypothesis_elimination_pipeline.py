import unittest

import structure.theory_observation_pipeline as observation_pipeline_module
from structure.theory_observation_pipeline import ObservationDerivedPipeline
from structure.theory_observation import ObservationDerivedContext
from structure.theory_pipeline import run_observation_derived_pipeline


class TestObservationDerivedHypothesisElimination(unittest.TestCase):
    def setUp(self):
        self.points = (
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
        )
        self.pipeline = ObservationDerivedPipeline.from_points(self.points)

    def test_all_former_external_boundaries_are_projections_of_one_context(self):
        p = self.pipeline
        self.assertEqual(len(p.A_max), 15)  # Bell(4), theorem-level universe
        self.assertEqual(p.Gamma, p.A_max)
        self.assertEqual(tuple(m.name for m in p.M), ("point", "line", "plane"))
        self.assertEqual(len(p.G_B.edges), 6)
        self.assertTrue(p.C_R.finite)
        self.assertTrue(p.C_R.complete_ordered)
        self.assertEqual(len(p.Phi_X(p.world()).values), 23)

    def test_candidate_family_is_finite_nonempty_and_quotient_compatible(self):
        family = self.pipeline.context.candidates
        self.assertTrue(family.blocks)
        self.assertTrue(family.is_maximal())
        self.assertEqual(set(self.pipeline.Gamma), set(self.pipeline.A_max))

    def test_stage2d_world_representation_use_observation_context(self):
        p = self.pipeline
        world = p.world()
        energy = p.energy
        representation = p.representation()

        self.assertIs(world.observation_context, p.context)
        self.assertGreaterEqual(energy.observation.scale, 1.0)
        self.assertEqual(len(representation.values), 23)
        self.assertEqual(representation, p.Phi_X(world))
        self.assertTrue(all(result.materializable for result in p.unit_formations if result.unit in world.units))

    def test_selection_is_after_stage2e_and_not_from_a_search(self):
        p = self.pipeline
        selected = p.select_partition()
        self.assertIn(selected, p.partitions)
        self.assertEqual(float(p.energy(selected)), min(float(p.energy(q)) for q in p.partitions))
        self.assertTrue(set(p.A_search).issubset(set(p.Gamma)))
        self.assertNotEqual(p.A_search, p.Gamma)

    def test_canonical_pipeline_does_not_call_a_search(self):
        original = observation_pipeline_module.A_search
        try:
            observation_pipeline_module.A_search = lambda *_args, **_kwargs: (_ for _ in ()).throw(
                AssertionError("A_search must not be called by the canonical pipeline")
            )
            result = run_observation_derived_pipeline(self.points)
            self.assertGreaterEqual(result.world.unit_count, 1)
            self.assertEqual(len(result.representation.values), 23)
        finally:
            observation_pipeline_module.A_search = original

    def test_derived_margin_is_observation_statistic(self):
        p = self.pipeline
        margin = p.derived_margin()
        self.assertGreaterEqual(margin, 0.0)
        self.assertEqual(margin, p.energy.derived_separation_margin(p.context.materialize_partitions()))

    def test_permuting_observation_does_not_change_boundary_cardinalities(self):
        p = self.pipeline
        permuted = ObservationDerivedPipeline.from_points((
            self.points[2], self.points[0], self.points[3], self.points[1]
        ))
        self.assertEqual(len(p.A_max), len(permuted.A_max))
        self.assertEqual(len(p.Gamma), len(permuted.Gamma))
        self.assertEqual(len(p.M), len(permuted.M))
        self.assertEqual(len(p.G_B.edges), len(permuted.G_B.edges))
        self.assertEqual(len(p.C_R), len(permuted.C_R))
        self.assertEqual(len(p.representation().values), len(permuted.representation().values))

    def test_context_can_be_constructed_directly_from_observation(self):
        context = ObservationDerivedContext.from_points(self.points)
        self.assertEqual(len(context.a_max), 15)
        self.assertEqual(len(context.gamma), 15)
        self.assertEqual(len(context.model_family), 3)
        self.assertEqual(len(context.boundary_graph.edges), 6)
        self.assertEqual(len(context.materialize_partitions()), 15)

    def test_context_owns_relation_domain_and_representation_map(self):
        p = self.pipeline
        selected = p.selected_units
        domain = p.context.relation_domain(selected)
        self.assertIs(domain.observation, p.X)
        self.assertEqual(domain.units, selected)
        self.assertEqual(len(domain), len(selected) * (len(selected) - 1))
        self.assertTrue(domain.is_quotient_compatible())
        phi = p.context.representation_map()
        self.assertIs(phi.context, p.context)
        self.assertEqual(phi(p.world()), p.representation())

    def test_proper_subcandidate_family_is_complete(self):
        p = self.pipeline
        candidate = p.context.unit_candidates[-1]  # full support
        subcandidates = p.S_X(candidate)
        self.assertEqual(len(subcandidates), 2 ** 4 - 2)
        supports = {tuple(u.indices) for u in subcandidates}
        self.assertNotIn(tuple(candidate.indices), supports)
        self.assertTrue((0,) in supports and (0, 1, 2) in supports)


if __name__ == "__main__":
    unittest.main()
