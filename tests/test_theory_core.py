import unittest

from structure.theory_core import Partition, TheoryUnit, evaluate_energy, select_minimizer


class TestTheoryCore(unittest.TestCase):
    def make_partition(self, groups):
        units = tuple(
            TheoryUnit(tuple(group), "candidate", {})
            for group in groups
        )
        universe = tuple(sorted(i for group in groups for i in group))
        return Partition(units, universe)

    def test_partition_is_disjoint_and_complete(self):
        partition = self.make_partition(((0, 1), (2, 3)))
        self.assertTrue(partition.is_partition)

    def test_empty_unit_is_rejected(self):
        with self.assertRaises(ValueError):
            TheoryUnit((), "candidate", {})

    def test_overlapping_units_are_rejected(self):
        with self.assertRaises(ValueError):
            self.make_partition(((0, 1), (1, 2)))

    def test_incomplete_partition_is_rejected(self):
        with self.assertRaises(ValueError):
            Partition((TheoryUnit((0,), "candidate", {}),), (0, 1))

    def test_energy_is_external(self):
        partition = self.make_partition(((0,), (1,)))
        self.assertEqual(evaluate_energy(partition, lambda p: 3.5), 3.5)

    def test_argmin_selects_from_explicit_candidates(self):
        p0 = self.make_partition(((0,), (1,)))
        p1 = self.make_partition(((0, 1),))
        result = select_minimizer(
            (p0, p1),
            lambda p: 0.0 if len(p.units) == 1 else 1.0,
        )
        self.assertIs(result, p1)


if __name__ == "__main__":
    unittest.main()
