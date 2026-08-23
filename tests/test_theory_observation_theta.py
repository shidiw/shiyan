import unittest

from structure.theory_energy_model import (
    GeometricModel,
    Observation3D,
    Stage2DEnergy,
    WeightedObservationGraph,
)
from structure.theory_observation_theta import (
    observation_theta,
    observation_unit,
    relabel_observation_unit,
    theta_injective,
    theta_signature,
)
from structure.theory_pipeline import select_stage2d_partition


class TestObservationDerivedTheta(unittest.TestCase):
    def setUp(self):
        self.X = Observation3D(
            points=((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 2.0, 0.0))
        )

    def test_theta_is_finite_and_complete(self):
        theta = observation_theta(self.X, (2, 0))
        self.assertEqual(theta["cardinality"], 2)
        self.assertEqual(theta["signature"], ((0.0, 0.0, 0.0), (0.0, 2.0, 0.0)))

    def test_theta_is_invariant_to_index_order(self):
        self.assertEqual(observation_theta(self.X, (0, 2)), observation_theta(self.X, (2, 0)))

    def test_theta_is_strictly_injective_on_distinct_geometric_blocks(self):
        u = observation_unit(self.X, (0, 1))
        v = observation_unit(self.X, (0, 2))
        self.assertNotEqual(theta_signature(u), theta_signature(v))
        self.assertFalse(theta_injective(u, v))

    def test_non_simple_observation_is_outside_strict_injectivity_domain(self):
        X = Observation3D(points=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
        with self.assertRaises(ValueError):
            observation_unit(X, (0,))

    def test_relabeling_preserves_theta(self):
        permutation = {0: 2, 1: 0, 2: 1}
        original = observation_unit(self.X, (0, 2))
        relabeled = relabel_observation_unit(self.X, (0, 2), permutation)
        self.assertEqual(theta_signature(original), theta_signature(relabeled))

    def test_stage2d_returns_units_with_observation_theta(self):
        graph = WeightedObservationGraph(
            edges=((0, 1, 1.0), (1, 2, 1.0), (0, 2, 1.0)),
            universe_size=3,
        )
        model = GeometricModel(
            name="point-model",
            squared_distance=lambda p: 0.0,
            complexity=0.0,
        )
        energy = Stage2DEnergy(
            observation=self.X,
            models=(model,),
            boundary_graph=graph,
            lambda_complexity=0.0,
            lambda_boundary=0.0,
        )
        partition = select_stage2d_partition(self.X, energy)
        for unit in partition.units:
            self.assertEqual(
                unit.attributes["signature"],
                tuple(sorted(self.X.points[i] for i in unit.indices)),
            )


if __name__ == "__main__":
    unittest.main()
