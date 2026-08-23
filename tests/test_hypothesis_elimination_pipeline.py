import unittest

from structure.theory_observation_pipeline import ObservationDerivedPipeline
from structure.theory_observation import ObservationDerivedContext


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
        self.assertTrue(p.Gamma)
        self.assertLessEqual(len(p.Gamma), len(p.A_max))
        self.assertEqual(tuple(m.name for m in p.M), ("point", "line", "plane"))
        self.assertEqual(len(p.G_B.edges), 6)
        self.assertEqual(len(p.C_R), len(p.selected_units) * (len(p.selected_units) - 1))
        self.assertEqual(len(p.Phi_X(p.world()).values), 23)

    def test_candidate_family_is_finite_nonempty_and_quotient_compatible(self):
        family = self.pipeline.context.candidates
        self.assertTrue(family.blocks)
        self.assertTrue(family.is_maximal())  # A_max remains the mathematical family
        self.assertTrue(set(self.pipeline.Gamma).issubset(set(self.pipeline.A_max)))

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
        self.assertEqual(p.A_search, p.Gamma)

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
        self.assertEqual(len(context.gamma), 3)
        self.assertEqual(len(context.model_family), 3)
        self.assertEqual(len(context.boundary_graph.edges), 6)
        self.assertEqual(len(context.materialize_partitions()), 3)


if __name__ == "__main__":
    unittest.main()
