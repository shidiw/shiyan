import unittest

from structure.theory_observation import ObservationDerivedContext


class TestHypothesisElimination(unittest.TestCase):
    """Regression contract for X-only provenance of the theory-facing path."""

    def setUp(self):
        self.points = (
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
        )
        self.context = ObservationDerivedContext.from_points(self.points)

    def test_six_former_external_boundaries_are_x_derived(self):
        # Gamma(X) is the frozen computational subfamily; A_max(X) is the
        # complete theorem-level admissible universe.  The correct contract is
        # Gamma(X) subset A_max(X), not equality.
        self.assertTrue(set(self.context.gamma).issubset(set(self.context.a_max)))
        self.assertEqual(self.context.models.observation, self.context.observation)
        self.assertEqual(self.context.boundary.observation, self.context.observation)
        self.assertTrue(self.context.unit_candidates)
        self.assertTrue(self.context.relation_candidates(2))

        candidate = self.context.unit_candidates[3]
        self.assertTrue(self.context.neighborhood_rule(candidate).alternatives)
        self.assertEqual(
            self.context.proper_subcandidates(candidate),
            tuple(self.context.proper_subcandidates(candidate)),
        )

    def test_stage2d_is_bound_to_the_same_context(self):
        energy = self.context.stage2d_energy()
        self.assertIs(energy.observation_context, self.context)
        self.assertEqual(energy.models, self.context.model_family)
        self.assertEqual(energy.boundary_graph, self.context.boundary_graph)

    def test_world_and_phi_use_context_provenance(self):
        partition = self.context.materialize_partitions()[0]
        world = self.context.build_world(partition)
        self.assertIs(world.observation_context, self.context)
        relations = self.context.form_relations(partition.units)
        self.assertEqual(relations.unit_count, world.unit_count)
        representation = self.context.phi_x(world)
        self.assertEqual(len(representation.as_tuple()), 23)

    def test_rebuilding_context_from_same_x_is_deterministic(self):
        other = ObservationDerivedContext.from_points(self.points)
        self.assertEqual(self.context.a_max, other.a_max)
        self.assertEqual(self.context.gamma, other.gamma)
        self.assertEqual(self.context.model_family, other.model_family)
        self.assertEqual(self.context.boundary_graph, other.boundary_graph)
        self.assertEqual(self.context.unit_candidates, other.unit_candidates)


if __name__ == "__main__":
    unittest.main()
