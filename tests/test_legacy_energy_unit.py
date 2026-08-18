import unittest

import numpy as np

from structure.energy import StructureEnergy
from structure.graph_cluster import GraphStructuralCluster
from structure.unit import StructuralUnit


class LegacyEnergyRegressionTests(unittest.TestCase):
    """Characterize historical behavior; these are not theory claims."""

    def test_default_energy_hyperparameters_are_preserved(self):
        energy = StructureEnergy()
        self.assertEqual(energy.lambda_complexity, 0.01)
        self.assertEqual(energy.gamma_boundary, 0.01)

    def test_plane_fit_is_zero_on_exact_plane(self):
        points = np.array(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 2.0, 0.0]],
            dtype=float,
        )
        unit = StructuralUnit(points, "plane")
        unit.parameters = {"normal": np.array([0.0, 0.0, 1.0]), "d": 0.0}
        self.assertAlmostEqual(StructureEnergy().fit_energy(unit), 0.0, places=12)

    def test_sphere_fit_is_zero_on_exact_sphere(self):
        points = np.array(
            [[2, 0, 0], [-2, 0, 0], [0, 2, 0], [0, -2, 0], [0, 0, 2], [0, 0, -2]],
            dtype=float,
        )
        unit = StructuralUnit(points, "sphere")
        unit.parameters = {"center": np.zeros(3), "radius": 2.0}
        self.assertAlmostEqual(StructureEnergy().fit_energy(unit), 0.0, places=12)

    def test_cylinder_fit_is_zero_on_exact_axis_aligned_cylinder(self):
        points = np.array(
            [[2, 0, 0], [0, 2, 1], [-2, 0, 2], [0, -2, 3]],
            dtype=float,
        )
        unit = StructuralUnit(points, "cylinder")
        unit.parameters = {"center": np.zeros(3), "radius": 2.0}
        self.assertAlmostEqual(StructureEnergy().fit_energy(unit), 0.0, places=12)

    def test_complexity_dimension_mapping_is_preserved(self):
        energy = StructureEnergy()
        self.assertEqual(energy.complexity_energy(StructuralUnit(np.zeros((1, 3)), "plane")), 4)
        self.assertEqual(energy.complexity_energy(StructuralUnit(np.zeros((1, 3)), "sphere")), 4)
        self.assertEqual(energy.complexity_energy(StructuralUnit(np.zeros((1, 3)), "cylinder")), 5)
        self.assertEqual(energy.complexity_energy(StructuralUnit(np.zeros((1, 3)), "unknown")), 10)

    def test_boundary_is_centroid_radius_variance_in_legacy_implementation(self):
        points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]], dtype=float)
        unit = StructuralUnit(points, "unknown")
        # Both points are exactly 0.5 from the centroid, so legacy variance is zero.
        self.assertAlmostEqual(StructureEnergy().boundary_energy(unit), 0.0, places=12)

    def test_compute_sets_unit_energy_and_returns_components(self):
        points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]], dtype=float)
        unit = StructuralUnit(points, "plane")
        unit.parameters = {"normal": np.array([0.0, 1.0, 0.0]), "d": 0.0}
        result = StructureEnergy().compute(unit)
        self.assertEqual(set(result), {"total", "fit", "complexity", "boundary"})
        self.assertEqual(unit.energy, result["total"])
        self.assertAlmostEqual(result["total"], result["fit"] + 0.01 * result["complexity"] + 0.01 * result["boundary"])


class LegacyPartitionRegressionTests(unittest.TestCase):
    """Characterize graph-cluster behavior; this is not Stable Partition theory."""

    def test_default_partition_threshold_and_minimum_are_preserved(self):
        cluster = GraphStructuralCluster()
        self.assertEqual(cluster.threshold, 0.5)
        self.assertEqual(cluster.min_points, 50)

    def test_thresholded_components_form_units(self):
        points = np.arange(18, dtype=float).reshape(6, 3)
        graph = {
            "edges": np.array([[0, 1], [1, 2], [3, 4], [4, 5], [2, 3]]),
            "weights": np.array([0.9, 0.8, 0.9, 0.8, 0.2]),
        }
        units = GraphStructuralCluster(threshold=0.5, min_points=3).extract(points, graph)
        self.assertEqual(len(units), 2)
        self.assertEqual([u.size() for u in units], [3, 3])
        self.assertEqual([u.primitive for u in units], ["unknown", "unknown"])

    def test_min_points_filters_small_components(self):
        points = np.arange(12, dtype=float).reshape(4, 3)
        graph = {
            "edges": np.array([[0, 1], [2, 3]]),
            "weights": np.array([0.9, 0.9]),
        }
        units = GraphStructuralCluster(threshold=0.5, min_points=3).extract(points, graph)
        self.assertEqual(units, [])


class StructuralUnitRegressionTests(unittest.TestCase):
    """Characterize the current StructuralUnit container and fitters."""

    def test_container_and_center(self):
        points = np.array([[0.0, 0.0, 0.0], [2.0, 2.0, 2.0]], dtype=float)
        unit = StructuralUnit(points, "unknown", indices=np.array([4, 7]))
        self.assertEqual(unit.size(), 2)
        np.testing.assert_allclose(unit.center(), [1.0, 1.0, 1.0])
        np.testing.assert_array_equal(unit.indices, [4, 7])
        self.assertIsNone(unit.energy)

    def test_plane_parameter_estimation_recovers_plane(self):
        points = np.array(
            [[0, 0, 0], [1, 0, 0], [0, 1, 0], [2, 3, 0]], dtype=float
        )
        unit = StructuralUnit(points, "plane")
        unit.estimate_parameters()
        normal = unit.parameters["normal"]
        self.assertAlmostEqual(abs(float(normal[2])), 1.0, places=12)
        self.assertAlmostEqual(unit.parameters["d"], 0.0, places=12)

    def test_estimate_parameters_leaves_unknown_primitive_empty(self):
        unit = StructuralUnit(np.zeros((3, 3)), "unknown")
        unit.estimate_parameters()
        self.assertEqual(unit.parameters, {})


if __name__ == "__main__":
    unittest.main()
