import unittest

from structure.theory_candidates import (
    ObservationCandidateFamily,
    observation_candidate_family,
    relabel_blocks,
)
from structure.theory_energy_model import (
    GeometricModel,
    Observation3D,
    Stage2DEnergy,
    WeightedObservationGraph,
)


class TestObservationDerivedCandidates(unittest.TestCase):
    def test_a_max_is_complete_finite_partition_family(self):
        family = observation_candidate_family(((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)))
        self.assertEqual(len(family.a_max), 5)
        self.assertEqual(set(family.gamma), set(family.a_max))
        self.assertTrue(family.is_maximal())

    def test_non_empty_observation_is_non_empty_candidate_family(self):
        family = observation_candidate_family(((0.0, 0.0, 0.0),))
        self.assertEqual(family.gamma, (((0,),),))

    def test_empty_observation_is_rejected(self):
        with self.assertRaises(ValueError):
            observation_candidate_family(())

    def test_quotient_compatibility_under_relabeling(self):
        family = ObservationCandidateFamily.from_universe((0, 1, 2))
        permutation = {0: 2, 1: 0, 2: 1}
        mapped = {relabel_blocks(blocks, permutation) for blocks in family.gamma}
        self.assertEqual(mapped, set(family.gamma))
        self.assertTrue(family.is_quotient_compatible(permutation))

    def test_maximal_family_is_independent_of_point_values(self):
        a = observation_candidate_family(((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)))
        b = observation_candidate_family(((100.0, 5.0, -2.0), (-7.0, 3.0, 9.0)))
        self.assertEqual(set(a.gamma), set(b.gamma))

    def test_stage_2d_energy_can_select_from_gamma(self):
        observation = Observation3D(((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)))
        graph = WeightedObservationGraph(((0, 1, 1.0),), 2)
        model = GeometricModel(
            "origin",
            lambda point: point[0] ** 2 + point[1] ** 2 + point[2] ** 2,
            0.0,
        )
        energy = Stage2DEnergy(observation, (model,), graph, 1.0, 1.0)
        family = observation_candidate_family(observation.points)
        partitions = family.materialize()
        selected = min(partitions, key=energy)
        self.assertIn(tuple(sorted(tuple(unit.indices) for unit in selected.units)),
                      {((0,), (1,)), ((0, 1),)})
        self.assertEqual(len(partitions), 2)


if __name__ == "__main__":
    unittest.main()
