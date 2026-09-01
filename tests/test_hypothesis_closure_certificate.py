import unittest

from structure.theory_hypothesis_closure import certify_hypothesis_elimination
from structure.theory_observation_pipeline import ObservationDerivedPipeline


class TestHypothesisClosureCertificate(unittest.TestCase):
    def setUp(self):
        self.points = (
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
        )

    def test_final_observation_only_closure(self):
        certificate = certify_hypothesis_elimination(
            ObservationDerivedPipeline.from_points(self.points)
        )
        self.assertTrue(certificate.passed)
        self.assertEqual(certificate.observation_size, 4)
        self.assertEqual(certificate.a_max_size, 15)
        self.assertEqual(certificate.gamma_size, 15)
        self.assertEqual(certificate.model_count, 3)
        self.assertEqual(certificate.boundary_edge_count, 6)
        self.assertEqual(certificate.representation_dim, 23)

    def test_closure_is_stable_under_observation_relabeling(self):
        first = certify_hypothesis_elimination(
            ObservationDerivedPipeline.from_points(self.points)
        )
        second = certify_hypothesis_elimination(
            ObservationDerivedPipeline.from_points(
                (self.points[2], self.points[0], self.points[3], self.points[1])
            )
        )
        self.assertTrue(first.passed)
        self.assertTrue(second.passed)
        self.assertEqual(first.a_max_size, second.a_max_size)
        self.assertEqual(first.gamma_size, second.gamma_size)
        self.assertEqual(first.model_count, second.model_count)
        self.assertEqual(first.boundary_edge_count, second.boundary_edge_count)
        self.assertEqual(first.relation_candidate_count, second.relation_candidate_count)
        self.assertEqual(first.representation_dim, second.representation_dim)


if __name__ == "__main__":
    unittest.main()
