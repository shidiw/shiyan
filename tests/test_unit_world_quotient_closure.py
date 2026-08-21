import unittest

from structure.theory_core import Partition
from structure.theory_energy_model import Observation3D, GeometricModel, Stage2DEnergy, WeightedObservationGraph
from structure.theory_observation_theta import observation_unit
from structure.theory_relation import StructuralRelation
from structure.theory_unit_world_quotient import (
    build_world,
    energy_induced_equivalent,
    energy_profile,
    prove_unit_energy_equivalence_consistency,
    unit_quotient_equivalent,
    world_quotient_compatible,
)


class TestUnitWorldQuotientClosure(unittest.TestCase):
    def setUp(self):
        self.X = Observation3D(
            points=((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 2.0, 0.0))
        )
        graph = WeightedObservationGraph(
            edges=((0, 1, 1.0), (1, 2, 1.0), (0, 2, 1.0)),
            universe_size=3,
        )
        model = GeometricModel(
            name="zero",
            squared_distance=lambda p: 0.0,
            complexity=0.0,
        )
        self.energy = Stage2DEnergy(
            observation=self.X,
            models=(model,),
            boundary_graph=graph,
            lambda_complexity=0.0,
            lambda_boundary=0.0,
        )

    def test_p_to_u_to_r_to_w_is_explicit(self):
        u0 = observation_unit(self.X, (0,))
        u1 = observation_unit(self.X, (1, 2))
        partition = Partition(units=(u0, u1), universe=(0, 1, 2))
        relations = (StructuralRelation(0, 1, "adjacent", {"source": "explicit"}),)
        q = build_world(self.X, partition, relations, {"Phi": "explicit"})
        self.assertEqual(q.world.unit_count, 2)
        self.assertEqual(q.world.relation_count, 1)
        self.assertEqual(q.world.attributes["Phi"], "explicit")

    def test_world_chain_is_quotient_compatible(self):
        u0 = observation_unit(self.X, (0,))
        u1 = observation_unit(self.X, (1, 2))
        partition = Partition(units=(u0, u1), universe=(0, 1, 2))
        relations = (StructuralRelation(0, 1, "adjacent"),)
        permutation = {0: 2, 1: 0, 2: 1}
        self.assertTrue(world_quotient_compatible(self.X, partition, relations, {"Phi": "invariant"}, permutation))

    def test_scalar_energy_is_not_claimed_to_be_unit_injective(self):
        u0 = observation_unit(self.X, (0,))
        u1 = observation_unit(self.X, (1,))
        self.assertEqual(energy_profile(u0, self.X, self.energy), energy_profile(u1, self.X, self.energy))
        self.assertFalse(unit_quotient_equivalent(u0, u1))
        self.assertTrue(energy_induced_equivalent(u0, u1, self.X, self.energy))

    def test_complete_profile_separation_closes_energy_equivalence(self):
        u0 = observation_unit(self.X, (0,))
        u1 = observation_unit(self.X, (1,))
        context = (lambda u: float(u.indices[0]),)
        self.assertTrue(prove_unit_energy_equivalence_consistency((u0, u1), self.X, self.energy, context))


if __name__ == "__main__":
    unittest.main()
