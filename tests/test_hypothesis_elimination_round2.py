import unittest

from structure.theory_energy_model import ObservationEnergyParameters
from structure.theory_observation import ObservationDerivedContext
from structure.theory_semantic_observation import Q_X


class TestHypothesisEliminationRound2(unittest.TestCase):
    def setUp(self):
        self.points = (
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
        )
        self.context = ObservationDerivedContext.from_points(self.points)

    def test_model_universe_is_finite_deterministic_and_x_derived(self):
        first = self.context.models
        second = ObservationDerivedContext.from_points(self.points).models
        self.assertEqual(first.universe, second.universe)
        self.assertEqual(tuple(m.complexity for m in first.universe), (0.0, 1.0, 2.0))
        self.assertEqual(tuple(m.name for m in first.universe), ("point", "line", "plane"))
        self.assertTrue(first.is_deterministic_for(self.context.observation))
        self.assertTrue(first.is_quotient_compatible())

    def test_boundary_regularization_graph_is_canonical(self):
        boundary = self.context.boundary
        self.assertTrue(boundary.is_complete)
        self.assertTrue(boundary.is_quotient_compatible())
        self.assertGreater(boundary.total_weight, 0.0)
        self.assertEqual(len(boundary.graph.edges), 3)

    def test_unique_qx_is_frozen_and_x_derived(self):
        units = self.context.unit_candidates[:2]
        self.assertTrue(Q_X(units[0], units[1], self.context))
        relations = self.context.form_relations(units)
        self.assertEqual(relations.unit_count, 2)
        self.assertEqual(len(relations.relations), 2)
        self.assertTrue(all(r.relation_type == "semantic_proximity" for r in relations.relations))
        self.assertTrue(all(r.evidence["strength"] > 0.0 for r in relations.relations))

    def test_stage2d_has_no_external_theory_parameters(self):
        energy = self.context.stage2d_energy()
        params = ObservationEnergyParameters.from_observation(self.context.observation)
        self.assertEqual(energy.lambda_complexity, params.lambda_complexity)
        self.assertEqual(energy.lambda_boundary, params.lambda_boundary)
        self.assertEqual(energy.separation_margin, 0.0)

    def test_delta_x_is_derived_from_gamma_not_a_search_input(self):
        energy = self.context.stage2d_energy()
        candidates = self.context.materialize_partitions()
        result = energy.verify_derived_separation(candidates)
        self.assertEqual(result.requested_margin, result.minimum_gap)
        self.assertGreaterEqual(result.minimum_gap, 0.0)
        self.assertEqual(result.compared_pairs, 3)

    def test_relabeling_preserves_model_and_boundary_objects(self):
        relabeled = tuple(self.points[i] for i in (2, 0, 1))
        other = ObservationDerivedContext.from_points(relabeled)
        self.assertEqual(
            tuple(m.name for m in self.context.models.universe),
            tuple(m.name for m in other.models.universe),
        )
        self.assertEqual(len(self.context.boundary.graph.edges), len(other.boundary.graph.edges))
        self.assertAlmostEqual(self.context.boundary.total_weight, other.boundary.total_weight)
        self.assertEqual(len(self.context.gamma), len(other.gamma))


if __name__ == "__main__":
    unittest.main()
