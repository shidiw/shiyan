import unittest

from structure.theory_admissible import (
    AdmissiblePartitionFamily,
    select_admissible_minimizer,
)
from structure.theory_core import Partition, TheoryUnit


class TestTheoryAdmissiblePartitionFamily(unittest.TestCase):
    def make_partition(self, groups):
        units = tuple(TheoryUnit(tuple(group), attributes={}) for group in groups)
        universe = tuple(sorted(i for group in groups for i in group))
        return Partition(units, universe)

    def test_family_requires_at_least_one_partition(self):
        with self.assertRaises(ValueError):
            AdmissiblePartitionFamily(())

    def test_family_requires_one_common_universe(self):
        p0 = self.make_partition(((0,), (1,)))
        p1 = self.make_partition(((0,), (2,)))
        with self.assertRaises(ValueError):
            AdmissiblePartitionFamily((p0, p1))

    def test_minimizer_is_selected_from_explicit_family(self):
        p0 = self.make_partition(((0,), (1,)))
        p1 = self.make_partition(((0, 1),))
        family = AdmissiblePartitionFamily((p0, p1))
        result = select_admissible_minimizer(
            family,
            lambda partition: 0.0 if len(partition.units) == 1 else 1.0,
        )
        self.assertIs(result, p1)

    def test_family_does_not_construct_partitions(self):
        p0 = self.make_partition(((0,), (1,)))
        family = AdmissiblePartitionFamily((p0,))
        self.assertEqual(family.partitions, (p0,))
        self.assertEqual(family.universe, (0, 1))


if __name__ == "__main__":
    unittest.main()
