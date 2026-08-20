import unittest

from structure.theory_core import Partition, TheoryUnit
from structure.theory_existence import (
    has_materializable_witness,
    prove_finite_minimizer_exists,
)


class TestTheoryExistence(unittest.TestCase):
    def make_partition(self, groups):
        units = tuple(TheoryUnit(tuple(group), attributes={}) for group in groups)
        universe = tuple(sorted(i for group in groups for i in group))
        return Partition(units, universe)

    def test_nonempty_finite_family_has_an_attained_minimum(self):
        split = self.make_partition(((0,), (1,)))
        merged = self.make_partition(((0, 1),))
        result = prove_finite_minimizer_exists(
            (split, merged),
            lambda p: 2.0 if len(p.units) == 2 else 0.5,
        )
        self.assertIs(result.minimizer, merged)
        self.assertEqual(result.minimum_energy, 0.5)
        self.assertEqual(result.candidate_count, 2)

    def test_empty_family_cannot_support_existence_theorem(self):
        with self.assertRaises(ValueError):
            prove_finite_minimizer_exists((), lambda p: 0.0)

    def test_nonfinite_energy_breaks_the_hypothesis(self):
        candidate = self.make_partition(((0,),))
        with self.assertRaises(ValueError):
            prove_finite_minimizer_exists((candidate,), lambda p: float("nan"))

    def test_tie_returns_a_witness_without_claiming_uniqueness(self):
        first = self.make_partition(((0,), (1,)))
        second = self.make_partition(((0, 1),))
        result = prove_finite_minimizer_exists((first, second), lambda p: 1.0)
        self.assertIs(result.minimizer, first)

    def test_materializable_existence_requires_an_explicit_witness(self):
        candidate = self.make_partition(((0,),))
        self.assertTrue(has_materializable_witness((candidate,), lambda p: True))
        self.assertFalse(has_materializable_witness((candidate,), lambda p: False))
        self.assertFalse(has_materializable_witness((), lambda p: True))


if __name__ == "__main__":
    unittest.main()
