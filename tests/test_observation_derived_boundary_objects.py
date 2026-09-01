import unittest

from structure.theory_observation_pipeline import ObservationDerivedPipeline


class TestObservationDerivedBoundaryObjects(unittest.TestCase):
    def setUp(self):
        self.points = (
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
        )
        self.pipeline = ObservationDerivedPipeline.from_points(self.points)

    def test_all_boundaries_are_first_class_and_x_derived(self):
        p = self.pipeline
        b = p.boundaries

        self.assertEqual(b.context.observation, p.X)
        self.assertEqual(b.A, b.A_max)
        self.assertEqual(b.Gamma, b.A_max)
        self.assertEqual(tuple(m.name for m in b.M), ("point", "line", "plane"))
        self.assertTrue(b.G_B.is_complete)
        self.assertEqual(b.C_R.units, b.units)
        self.assertEqual(b.Phi_X.dimension, 23)
        self.assertTrue(b.finite_and_nonempty())
        self.assertTrue(b.quotient_compatible())

    def test_nx_and_sx_are_families_not_external_rules(self):
        p = self.pipeline
        b = p.boundaries
        candidate = b.units[-1]

        neighborhood = b.neighborhood(candidate)
        proper = b.proper_subcandidates(candidate)

        self.assertTrue(b.N_X.finite)
        self.assertTrue(b.S_X.finite)
        self.assertTrue(all(u.indices for u in neighborhood.alternatives))
        self.assertEqual(len(proper), 2 ** len(candidate.indices) - 2)

    def test_stage2d_consumes_exact_boundary_objects(self):
        p = self.pipeline
        b = p.boundaries
        e = p.energy

        self.assertEqual(e.observation, p.X)
        self.assertEqual(e.models, b.M)
        self.assertEqual(e.boundary_graph, b.G_B)
        self.assertIs(e.observation_context, b.context)

    def test_world_and_representation_consume_x_derived_c_r_and_phi(self):
        p = self.pipeline
        b = p.boundaries
        world = p.world()

        self.assertEqual(p.world_relation_domain.observation, p.X)
        self.assertEqual(p.world_relation_domain.units, world.units)
        self.assertIs(world.observation_context, b.context)
        self.assertEqual(b.Phi_X(world), p.representation())
        self.assertEqual(len(p.representation().values), 23)

    def test_boundary_object_cardinalities_survive_observation_relabeling(self):
        p = self.pipeline
        q = ObservationDerivedPipeline.from_points(
            (self.points[2], self.points[0], self.points[3], self.points[1])
        )

        self.assertEqual(len(p.boundaries.A), len(q.boundaries.A))
        self.assertEqual(len(p.boundaries.M), len(q.boundaries.M))
        self.assertEqual(len(p.boundaries.G_B.edges), len(q.boundaries.G_B.edges))
        self.assertEqual(len(p.boundaries.N_X), len(q.boundaries.N_X))
        self.assertEqual(len(p.boundaries.S_X), len(q.boundaries.S_X))
        self.assertEqual(len(p.boundaries.C_R), len(q.boundaries.C_R))
        self.assertEqual(p.boundaries.Phi_X.dimension, q.boundaries.Phi_X.dimension)


if __name__ == "__main__":
    unittest.main()
