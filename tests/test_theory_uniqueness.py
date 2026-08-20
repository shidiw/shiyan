import unittest

from structure.theory_core import Partition, TheoryUnit
from structure.theory_uniqueness import (
    is_unique_minimizer,
    prove_unique_minimizer,
)


class TestTheoryUniqueness(unittest.TestCase):
    def make_partition(self, groups):
        units = tuple(TheoryUnit(tuple(group), attributes={}) for group in groups)
        universe = tuple(sorted(i for group in groups for i in group))
        return Partition(units, universe)

    def test_strictly_lower_energy_is_unique(self):
        best = self.make_partition(((0, 1),))
        other = self.make_partition(((0,), (1,)))
        self.assertTrue(is_unique_minimizer(best, (other,), lambda p: 0.5 if len(p.units) == 1 else 2.0))
        result = prove_unique_minimizer(best, (other,), lambda p: 0.5 if len(p.units) == 1 else 2.0)
        self.assertTrue(result.unique)
        self.assertEqual(result.energy, 0.5)

    def test_equal_energy_is_not_unique(self):
        first = self.make_partition(((0,), (1,)))
        second = self.make_partition(((0, 1),))
        self.assertFalse(is_unique_minimizer(first, (second,), lambda p: 1.0))
        with self.assertRaises(ValueError):
            prove_unique_minimizer(first, (second,), lambda p: 1.0)

    def test_lower_energy_competitor_is_not_unique(self):
        candidate = self.make_partition(((0, 1),))
        competitor = self.make_partition(((0,), (1,)))
        # Candidate has one unit; competitor has two. The competitor must
        # explicitly receive the lower energy for this test to exercise the
        # strict-separation condition.
        self.assertFalse(is_unique_minimizer(candidate, (competitor,), lambda p: 2.0 if len(p.units) == 2 else 3.0))

    def test_nonfinite_energy_is_rejected(self):
        candidate = self.make_partition(((0,),))
        with self.assertRaises(ValueError):
            is_unique_minimizer(candidate, (), lambda p: float("inf"))


if __name__ == "__main__":
    unittest.main()
