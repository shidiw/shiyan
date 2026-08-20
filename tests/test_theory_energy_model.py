import unittest

from structure.theory_core import Partition, TheoryUnit
from structure.theory_energy_model import (
    GeometricModel,
    Observation3D,
    Stage2DEnergy,
    WeightedObservationGraph,
)


class TestStage2DEnergy(unittest.TestCase):
    def setUp(self):
        self.observation = Observation3D(
            (
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (0.0, 1.0, 0.0),
                (1.0, 1.0, 0.0),
            )
        )
        self.graph = WeightedObservationGraph(
            ((0, 1, 1.0), (0, 2, 1.0), (1, 3, 1.0), (2, 3, 1.0)),
            universe_size=4,
        )
        self.plane = GeometricModel(
            "plane",
            squared_distance=lambda p: p[2] ** 2,
            complexity=4.0,
        )
        self.offset = GeometricModel(
            "offset",
            squared_distance=lambda p: (p[2] - 1.0) ** 2,
            complexity=5.0,
        )
        self.energy = Stage2DEnergy(
            self.observation,
            (self.plane, self.offset),
            self.graph,
            lambda_complexity=0.0,
            lambda_boundary=1.0,
        )

    def partition(self, *groups):
        units = tuple(TheoryUnit(tuple(group), {}) for group in groups)
        return Partition(units, tuple(range(4)))

    def test_fit_is_normalized_by_observation_scale_and_point_count(self):
        unit = TheoryUnit((0, 1), {})
        self.assertEqual(self.energy.fit_energy(unit, self.plane), 0.0)

    def test_scale_invariance_of_homogeneous_fit(self):
        observation = Observation3D(
            (
                (0.0, 0.0, 0.5),
                (1.0, 0.0, 1.0),
                (0.0, 1.0, 1.5),
                (1.0, 1.0, 2.0),
            )
        )
        scaled = Observation3D(tuple(tuple(3.0 * value for value in p) for p in observation.points))
        model = GeometricModel("homogeneous", lambda p: p[2] ** 2, 0.0)
        graph = self.graph
        first = Stage2DEnergy(observation, (model,), graph, 0.0, 0.0)
        second = Stage2DEnergy(scaled, (model,), graph, 0.0, 0.0)
        unit = TheoryUnit((0, 1, 2, 3), {})
        self.assertAlmostEqual(first.fit_energy(unit, model), second.fit_energy(unit, model))

    def test_model_selection_is_explicit_and_complexity_is_part_of_unit_cost(self):
        energy = Stage2DEnergy(
            self.observation,
            (
                GeometricModel("cheap_bad", lambda p: 1.0, 0.0),
                GeometricModel("expensive_good", lambda p: 0.0, 2.0),
            ),
            self.graph,
            lambda_complexity=1.0,
            lambda_boundary=0.0,
        )
        unit = TheoryUnit((0, 1), {})
        self.assertAlmostEqual(energy.unit_energy(unit), 0.5)

    def test_boundary_is_normalized_cut_weight(self):
        one_unit = self.energy.boundary_energy(self.partition((0, 1, 2, 3)))
        two_units = self.energy.boundary_energy(self.partition((0, 1), (2, 3)))
        self.assertEqual(one_unit, 0.0)
        self.assertGreater(two_units, 0.0)
        self.assertLessEqual(two_units, 1.0)

    def test_total_energy_matches_fit_plus_complexity_plus_boundary(self):
        partition = self.partition((0, 1, 2, 3))
        self.assertEqual(self.energy(partition), 0.0)

    def test_zero_diameter_observation_is_rejected(self):
        with self.assertRaises(ValueError):
            Observation3D(((1.0, 1.0, 1.0),))

    def test_negative_weight_is_rejected(self):
        with self.assertRaises(ValueError):
            GeometricModel("bad", lambda p: 0.0, -1.0)

    def test_negative_or_nonfinite_squared_distance_is_rejected(self):
        unit = TheoryUnit((0, 1), {})
        negative = GeometricModel("negative", lambda p: -1.0, 0.0)
        nonfinite = GeometricModel("nonfinite", lambda p: float("nan"), 0.0)
        with self.assertRaises(ValueError):
            self.energy.fit_energy(unit, negative)
        with self.assertRaises(ValueError):
            self.energy.fit_energy(unit, nonfinite)

    def test_negative_unit_index_is_rejected(self):
        unit = TheoryUnit((-1,), {})
        with self.assertRaises(ValueError):
            self.energy.fit_energy(unit, self.plane)

    def test_duplicate_boundary_edge_is_rejected(self):
        with self.assertRaises(ValueError):
            WeightedObservationGraph(
                ((0, 1, 1.0), (0, 1, 2.0)),
                universe_size=4,
            )

    def test_partition_must_match_observation_index_universe(self):
        invalid = Partition((TheoryUnit((1,), {}),), (1,))
        with self.assertRaises(ValueError):
            self.energy(invalid)


if __name__ == "__main__":
    unittest.main()
