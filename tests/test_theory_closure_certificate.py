import unittest

from structure.theory_closure import audit_observation_context
from structure.theory_observation import ObservationDerivedContext


class TestTheoryClosureCertificate(unittest.TestCase):
    def setUp(self):
        self.context = ObservationDerivedContext.from_points(
            (
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (0.0, 1.0, 0.0),
            )
        )

    def test_all_observation_boundaries_are_closed(self):
        certificate = audit_observation_context(self.context)
        self.assertTrue(certificate.upstream_closed)
        self.assertTrue(certificate.observation_nonempty)
        self.assertTrue(certificate.candidate_nonempty)
        self.assertTrue(certificate.candidate_finite)
        self.assertTrue(certificate.candidate_quotient_compatible)
        self.assertTrue(certificate.model_family_finite)
        self.assertTrue(certificate.neighborhood_derived)
        self.assertTrue(certificate.proper_subcandidate_derived)
        self.assertTrue(certificate.boundary_graph_derived)
        self.assertTrue(certificate.relation_candidates_derived)
        self.assertTrue(certificate.phi_concrete)
        self.assertEqual(certificate.phi_dimension, 23)

    def test_separation_is_derived_not_caller_supplied(self):
        certificate = audit_observation_context(self.context)
        self.assertEqual(certificate.separation.requested_margin, certificate.separation.minimum_gap)
        self.assertGreaterEqual(certificate.separation.minimum_gap, 0.0)
        self.assertGreaterEqual(certificate.separation.compared_pairs, 1)

    def test_representation_claims_remain_bounded(self):
        certificate = audit_observation_context(self.context)
        self.assertFalse(certificate.dr_semantic_completeness_established)
        self.assertIsNone(certificate.phi_injective_on_checked_worlds)


if __name__ == "__main__":
    unittest.main()
