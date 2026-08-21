import unittest

from structure.theory_core import Partition, TheoryUnit
from structure.theory_energy_model import (
    GeometricModel,
    Observation3D,
    Stage2DEnergy,
    WeightedObservationGraph,
    partition_quotient_key,
    structurally_equivalent_partitions,
)
from structure.theory_unit import StructuralUnit
from structure.theory_unit_formation import has_energy_margin
from structure.theory_uniqueness import is_unique_minimizer


class TestEnergySeparationMargin(unittest.TestCase):
    def setUp(self):
        observation = Observation3D(
            (
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (0.0, 1.0, 0.0),
                (1.0, 1.0, 0.0),
            )
        )
        graph = WeightedObservationGraph(
            ((0, 1, 1.0), (0, 2, 1.0), (1, 3, 1.0), (2, 3, 1.0)),
            universe_size=4,
        )
        plane = GeometricModel("plane", lambda p: p[2] ** 2, 0.0)
        self.energy = Stage2DEnergy(
            observation,
            (plane,),
            graph,
            lambda_complexity=0.0,
            lambda_boundary=1.0,
            separation_margin=0.5,
        )

    @staticmethod
    def partition(*groups):
        units = tuple(TheoryUnit(tuple(group), {}) for group in groups)
        return Partition(units, (0, 1, 2, 3))

    def test_partition_quotient_ignores_unit_order(self):
        first = self.partition((0, 1), (2, 3))
        second = self.partition((2, 3), (0, 1))
        self.assertTrue(structurally_equivalent_partitions(first, second))
        self.assertEqual(partition_quotient_key(first), partition_quotient_key(second))
        self.assertEqual(self.energy(first), self.energy(second))
        self.assertEqual(self.energy.energy_gap(first, second), 0.0)

    def test_positive_margin_is_verified_on_quotient_distinct_candidates(self):
        one_unit = self.partition((0, 1, 2, 3))
        two_units = self.partition((0, 1), (2, 3))
        result = self.energy.verify_separation_margin((one_unit, two_units))
        self.assertTrue(result.satisfied)
        self.assertEqual(result.compared_pairs, 1)
        self.assertAlmostEqual(result.minimum_gap, 1.0)
        self.assertEqual(result.requested_margin, 0.5)
        self.assertTrue(self.energy.require_separation_margin((one_unit, two_units)).satisfied)

    def test_margin_failure_is_reported_instead_of_manufactured(self):
        one_unit = self.partition((0, 1, 2, 3))
        two_units = self.partition((0, 1), (2, 3))
        result = self.energy.verify_separation_margin((one_unit, two_units), margin=1.1)
        self.assertFalse(result.satisfied)
        self.assertAlmostEqual(result.minimum_gap, 1.0)
        with self.assertRaises(ValueError):
            self.energy.require_separation_margin((one_unit, two_units), margin=1.1)

    def test_stage2g_consumes_the_same_one_sided_margin_and_respects_quotient(self):
        best = self.partition((0, 1, 2, 3))
        competitor = self.partition((0, 1), (2, 3))
        reordered_equivalent = self.partition((2, 3), (0, 1))
        equivalence = structurally_equivalent_partitions
        self.assertTrue(is_unique_minimizer(best, (competitor,), self.energy, margin=0.5, equivalence=equivalence))
        self.assertFalse(is_unique_minimizer(best, (competitor,), self.energy, margin=1.1, equivalence=equivalence))
        self.assertTrue(is_unique_minimizer(best, (reordered_equivalent,), self.energy, margin=0.5, equivalence=equivalence))

    def test_stage2e_can_require_an_explicit_unit_margin(self):
        unit = StructuralUnit((0, 1), {})
        competitor = StructuralUnit((0,), {})
        energy = lambda u: 0.0 if u.indices == (0, 1) else 1.0
        self.assertTrue(has_energy_margin(unit, (competitor,), energy, 0.5))
        self.assertFalse(has_energy_margin(unit, (competitor,), energy, 1.1))
        self.assertFalse(has_energy_margin(unit, (), energy, 0.5))


if __name__ == "__main__":
    unittest.main()
