import unittest

from structure.theory_core import StructuralUnit
from structure.theory_observation import ObservationDerivedContext
from structure.theory_energy_model import Stage2DEnergy
from structure.theory_pipeline import run_observation_derived_pipeline
from structure.theory_representation import phi_x
from structure.theory_relation_formation import form_observation_relations
from structure.theory_world import StructuralWorld


class TestObservationDerivedClosure(unittest.TestCase):
    def setUp(self):
        self.points = (
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
        )
        self.context = ObservationDerivedContext.from_points(self.points)

    def test_all_external_boundaries_are_functions_of_x(self):
        self.assertTrue(self.context.a_max)
        self.assertEqual(self.context.gamma, self.context.a_max)
        self.assertEqual(len(self.context.model_family), 3)
        self.assertEqual(len(self.context.boundary_graph.edges), 3)
        self.assertTrue(self.context.unit_candidates)
        self.assertTrue(self.context.relation_candidates(2))

    def test_a_max_is_finite_and_non_empty(self):
        self.assertEqual(len(self.context.a_max), 5)
        self.assertEqual(len(self.context.gamma), 5)

    def test_boundary_graph_is_observation_derived(self):
        weights = [weight for _, _, weight in self.context.boundary_graph.edges]
        self.assertEqual(len(weights), 3)
        self.assertTrue(all(weight > 0.0 for weight in weights))

    def test_neighborhood_and_subcandidate_families_are_finite(self):
        candidate = self.context.unit_candidates[3]
        neighborhood = self.context.neighborhood_rule(candidate)
        subcandidates = self.context.proper_subcandidates(candidate)
        self.assertTrue(neighborhood.alternatives)
        self.assertEqual(len(subcandidates), 2)

    def test_stage2d_consumes_observation_derived_m_and_boundary(self):
        energy = Stage2DEnergy.from_observation(self.context)
        self.assertIs(energy.observation_context, self.context)
        self.assertEqual(energy.models, self.context.model_family)
        self.assertEqual(energy.boundary_graph, self.context.boundary_graph)
        partition = self.context.materialize_partitions()[0]
        self.assertTrue(energy(partition) >= 0.0)

    def test_relation_candidates_and_world_are_observation_derived(self):
        partition = self.context.materialize_partitions()[0]
        relations = form_observation_relations(partition.units, self.context)
        world = StructuralWorld(partition.units, relations.relations, {})
        self.assertEqual(relations.unit_count, world.unit_count)
        self.assertEqual(world.relation_count, world.unit_count * (world.unit_count - 1))

    def test_phi_x_is_well_defined_and_23_dimensional(self):
        partition = self.context.materialize_partitions()[0]
        relations = form_observation_relations(partition.units, self.context)
        world = StructuralWorld(partition.units, relations.relations, {})
        representation = phi_x(world, self.context)
        self.assertEqual(len(representation.as_tuple()), 23)
        self.assertTrue(all(value == value for value in representation.as_tuple()))

    def test_phi_x_is_unit_label_quotient_compatible(self):
        first_units = (StructuralUnit((0,), {}), StructuralUnit((1, 2), {}))
        second_units = tuple(reversed(first_units))
        first_relations = form_observation_relations(first_units, self.context)
        second_relations = form_observation_relations(second_units, self.context)
        first_world = StructuralWorld(first_units, first_relations.relations, {})
        second_world = StructuralWorld(second_units, second_relations.relations, {})
        self.assertEqual(phi_x(first_world, self.context).as_tuple(), phi_x(second_world, self.context).as_tuple())

    def test_end_to_end_observation_derived_pipeline(self):
        result = run_observation_derived_pipeline(self.points)
        self.assertGreaterEqual(result.world.unit_count, 1)
        self.assertEqual(len(result.representation.as_tuple()), 23)

    def test_observation_relabeling_preserves_family_cardinality(self):
        permutation = (2, 0, 1)
        relabeled = tuple(self.points[i] for i in permutation)
        other = ObservationDerivedContext.from_points(relabeled)
        self.assertEqual(len(other.a_max), len(self.context.a_max))
        self.assertEqual(len(other.unit_candidates), len(self.context.unit_candidates))
        self.assertEqual(len(other.boundary_graph.edges), len(self.context.boundary_graph.edges))
        self.assertEqual(len(other.relation_candidates(3)), len(self.context.relation_candidates(3)))


if __name__ == "__main__":
    unittest.main()
