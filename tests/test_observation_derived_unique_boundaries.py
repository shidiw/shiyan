import inspect
import unittest

from structure.theory_candidate_search import Gamma_X
from structure.theory_energy_model import Stage2DEnergy
from structure.theory_observation import ObservationDerivedContext
from structure.theory_observation_pipeline import ObservationDerivedPipeline
from structure.theory_semantic_relation import form_observation_semantic_relations
from structure.theory_representation import phi_x


class TestObservationDerivedUniqueBoundaries(unittest.TestCase):
    def setUp(self):
        self.points = (
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
        )
        self.pipeline = ObservationDerivedPipeline.from_points(self.points)
        self.context = self.pipeline.context

    def test_gamma_has_no_external_strategy_boundary(self):
        signature = inspect.signature(Gamma_X)
        self.assertEqual(tuple(signature.parameters), ("observation",))
        self.assertEqual(Gamma_X(self.context.observation), self.pipeline.Gamma)

    def test_all_boundaries_are_reconstructed_deterministically_from_x(self):
        other = ObservationDerivedContext.from_points(self.points)
        self.assertEqual(self.context.a_max, other.a_max)
        self.assertEqual(self.context.gamma, other.gamma)
        self.assertEqual(self.context.model_family, other.model_family)
        self.assertEqual(self.context.boundary_graph, other.boundary_graph)
        self.assertEqual(self.context.unit_candidates, other.unit_candidates)

        for unit in self.context.unit_candidates:
            self.assertEqual(self.context.neighborhood_rule(unit), other.neighborhood_rule(unit))
            self.assertEqual(self.context.proper_subcandidates(unit), other.proper_subcandidates(unit))

    def test_stage2d_consumes_the_unique_m_and_gb_objects(self):
        energy = Stage2DEnergy.from_observation(self.context)
        self.assertIs(energy.observation_context, self.context)
        self.assertEqual(energy.models, self.context.model_family)
        self.assertEqual(energy.boundary_graph, self.context.boundary_graph)

    def test_canonical_relation_materializer_consumes_cr(self):
        units = self.context.materialize_partitions()[1].units
        expected = set(self.context.relation_candidate_domain(units))
        self.assertEqual(expected, {(i, j) for i in range(len(units)) for j in range(len(units)) if i != j})
        relations = form_observation_semantic_relations(units, self.context)
        actual = {(r.source, r.target) for r in relations.relations}
        self.assertTrue(actual.issubset(expected))

    def test_canonical_relation_materializer_rejects_injected_cr(self):
        class BadContext:
            observation = self.context.observation
            model_family = self.context.model_family

            def relation_candidates(self, count):
                return ()

        units = self.context.materialize_partitions()[1].units
        with self.assertRaises(ValueError):
            form_observation_semantic_relations(units, BadContext())

    def test_phi_x_rejects_world_from_another_observation_context(self):
        world = self.pipeline.world()
        other = ObservationDerivedContext.from_points(self.points)
        with self.assertRaises(ValueError):
            phi_x(world, other)

    def test_full_chain_uses_the_same_context(self):
        world = self.pipeline.world()
        representation = self.pipeline.representation()
        self.assertIs(world.observation_context, self.context)
        self.assertEqual(representation, phi_x(world, self.context))
        self.assertEqual(len(representation.values), 23)

    def test_audit_reports_no_external_canonical_boundary(self):
        audit = self.pipeline.audit()
        self.assertFalse(audit["A_search_used_by_pipeline"])
        self.assertTrue(audit["World_uses_C_R"])
        self.assertTrue(audit["World_uses_unique_Q_X"])
        self.assertTrue(audit["World_derived_from_X"])
        self.assertEqual(audit["Phi_X_dimension"], 23)


if __name__ == "__main__":
    unittest.main()
