import unittest

from structure.theory_core import Partition, TheoryUnit
from structure.theory_partition import select_stable_partition


class TestTheoryPartition(unittest.TestCase):
    def make(self, groups):
        units = tuple(TheoryUnit(tuple(g), "candidate", {}) for g in groups)
        universe = tuple(sorted(i for g in groups for i in g))
        return Partition(units, universe)

    def test_selects_global_minimum_from_explicit_candidates(self):
        split = self.make(((0,), (1,)))
        merged = self.make(((0, 1),))
        result = select_stable_partition(
            (split, merged),
            lambda p: 2.0 if len(p.units) == 2 else 0.5,
        )
        self.assertIs(result.partition, merged)
        self.assertEqual(result.energy.value, 0.5)
        self.assertEqual(result.candidate_count, 2)

    def test_tie_is_deterministic_without_claiming_uniqueness(self):
        first = self.make(((0,), (1,)))
        second = self.make(((0, 1),))
        result = select_stable_partition((first, second), lambda p: 1.0)
        self.assertIs(result.partition, first)

    def test_empty_admissible_set_is_rejected(self):
        with self.assertRaises(ValueError):
            select_stable_partition((), lambda p: 0.0)


if __name__ == "__main__":
    unittest.main()
