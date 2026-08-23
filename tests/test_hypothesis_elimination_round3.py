import unittest

from structure.theory_closed_form import ObservationDerivedBoundaries


class TestHypothesisEliminationRound3(unittest.TestCase):
    """Strict regression contract: all six former boundaries are X-derived."""

    def setUp(self):
        self.points = (
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
        )
        self.closed = ObservationDerivedBoundaries.from_points(self.points)

    def test_all_boundaries_have_one_provenance_source(self):
        self.assertTrue(self.closed.A_max)
        self.assertTrue(self.closed.Gamma)
        self.assertTrue(self.closed.M)
        self.assertTrue(self.closed.G_B.edges)
        self.assertTrue(self.closed.units)
        self.assertTrue(self.closed.C_R)
        self.assertTrue(self.closed.is_closed())

    def test_no_boundary_is_injected_into_stage2d_world_or_phi(self):
        energy = self.closed.energy
        world = self.closed.world()
        representation = self.closed.representation()

        self.assertIs(energy.observation_context, self.closed.context)
        self.assertIs(world.observation_context, self.closed.context)
        self.assertEqual(len(representation.values), 23)

    def test_rebuilding_from_same_observation_is_deterministic(self):
        other = ObservationDerivedBoundaries.from_points(self.points)
        self.assertEqual(self.closed.A_max, other.A_max)
        self.assertEqual(self.closed.Gamma, other.Gamma)
        self.assertEqual(self.closed.M, other.M)
        self.assertEqual(self.closed.G_B, other.G_B)
        self.assertEqual(self.closed.units, other.units)
        self.assertEqual(self.closed.C_R, other.C_R)
        self.assertEqual(self.closed.representation().values, other.representation().values)

    def test_observation_relabeling_preserves_boundary_cardinalities(self):
        relabeled = tuple(self.points[i] for i in (2, 0, 1))
        other = ObservationDerivedBoundaries.from_points(relabeled)
        self.assertEqual(len(self.closed.A_max), len(other.A_max))
        self.assertEqual(len(self.closed.Gamma), len(other.Gamma))
        self.assertEqual(len(self.closed.M), len(other.M))
        self.assertEqual(len(self.closed.G_B.edges), len(other.G_B.edges))
        self.assertEqual(len(self.closed.units), len(other.units))
        self.assertEqual(len(self.closed.C_R), len(other.C_R))


if __name__ == "__main__":
    unittest.main()
