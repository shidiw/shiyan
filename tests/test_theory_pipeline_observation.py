import unittest

from structure.theory_candidates import observation_candidate_family, relabel_blocks
from structure.theory_energy_model import (
    GeometricModel,
    Observation3D,
    Stage2DEnergy,
    WeightedObservationGraph,
)
from structure.theory_pipeline import build_gamma, select_stage2d_partition


class TestObservationStage2DPipeline(unittest.TestCase):
    def make_energy(self, observation):
        graph = WeightedObservationGraph(
            tuple((i, i + 1, 1.0) for i in range(len(observation.points) - 1)),
            len(observation.points),
        )
        model = GeometricModel(
            "origin",
            lambda point: sum(value * value for value in point),
            0.0,
        )
        return Stage2DEnergy(observation, (model,), graph, 1.0, 1.0)

    def test_gamma_is_the_candidate_domain_consumed_by_stage_2d(self):
        observation = Observation3D(((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)))
        gamma = build_gamma(observation.points)
        self.assertEqual(set(gamma.gamma), set(observation_candidate_family(observation.points).a_max))
        selected = select_stage2d_partition(observation, self.make_energy(observation))
        self.assertIn(tuple(sorted(tuple(u.indices) for u in selected.units)),
                      {((0,), (1,)), ((0, 1),)})

    def test_gamma_is_quotient_compatible(self):
        observation = Observation3D(((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)))
        gamma = build_gamma(observation.points)
        permutation = {0: 2, 1: 0, 2: 1}
        self.assertTrue(gamma.is_quotient_compatible(permutation))
        mapped = {relabel_blocks(p, permutation) for p in gamma.gamma}
        self.assertEqual(mapped, set(gamma.gamma))

    def test_stage_2d_energy_cannot_use_a_partition_outside_gamma(self):
        observation = Observation3D(((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)))
        energy = self.make_energy(observation)
        gamma = build_gamma(observation.points)
        self.assertEqual(len(gamma.materialize()), 2)
        for partition in gamma.materialize():
            self.assertEqual(energy.observation, observation)
            self.assertIsInstance(energy(partition), float)


if __name__ == "__main__":
    unittest.main()
