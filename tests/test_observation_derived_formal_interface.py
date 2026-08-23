import unittest

from structure.theory_closed_form import ObservationDerivedBoundaries
from structure.theory_observation_interface import ObservationDerivedTheoryInterface


class TestObservationDerivedFormalInterface(unittest.TestCase):
    """Release contract for the frozen X-derived theorem boundary."""

    def setUp(self):
        self.points = (
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
        )
        self.theory = ObservationDerivedBoundaries.from_points(self.points)

    def test_concrete_bundle_implements_formal_interface(self):
        self.assertIsInstance(self.theory, ObservationDerivedTheoryInterface)

    def test_all_former_external_boundaries_are_read_only_interface_members(self):
        required = (
            "X", "A_max", "Gamma", "M", "G_B", "units", "N_X", "S_X",
            "C_R", "Phi_X", "energy", "world", "representation", "is_closed",
        )
        for name in required:
            self.assertTrue(hasattr(self.theory, name), name)

    def test_interface_has_no_boundary_injection_constructor(self):
        # The only constructor path is from observation points.  A caller
        # cannot supply A_max/M/G_B/N_X/S_X/C_R/Phi_X independently.
        with self.assertRaises(TypeError):
            ObservationDerivedBoundaries(
                self.theory.context,
                self.theory.pipeline,
                A_max=(),
            )

    def test_stage2d_world_phi_share_the_same_provenance(self):
        energy = self.theory.energy
        world = self.theory.world()
        phi = self.theory.representation()
        self.assertIs(energy.observation_context, self.theory.context)
        self.assertIs(world.observation_context, self.theory.context)
        self.assertEqual(phi, self.theory.Phi_X(world))
        self.assertEqual(len(phi.values), 23)
        self.assertTrue(self.theory.is_closed())

    def test_reconstruction_from_same_x_is_exactly_deterministic(self):
        other = ObservationDerivedBoundaries.from_points(self.points)
        self.assertEqual(self.theory.A_max, other.A_max)
        self.assertEqual(self.theory.Gamma, other.Gamma)
        self.assertEqual(self.theory.M, other.M)
        self.assertEqual(self.theory.G_B, other.G_B)
        self.assertEqual(self.theory.C_R, other.C_R)
        self.assertEqual(self.theory.representation().values, other.representation().values)


if __name__ == "__main__":
    unittest.main()
