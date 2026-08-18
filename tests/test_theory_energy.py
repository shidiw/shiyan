import unittest

from structure.theory_core import Partition, TheoryUnit
from structure.theory_energy import StructuralEnergy, candidate_energy


class TestTheoryEnergy(unittest.TestCase):
    def partition(self):
        u = TheoryUnit((0, 1), "candidate", {})
        return Partition((u,), (0, 1))

    def test_energy_is_defined_by_supplied_functional(self):
        energy = StructuralEnergy(lambda p: len(p.units) + 0.5)
        result = energy(self.partition())
        self.assertEqual(result.value, 1.5)
        self.assertEqual(result.source, "theory")

    def test_unit_energy_is_external(self):
        u = TheoryUnit((0, 1), "candidate", {})
        result = candidate_energy(u, lambda unit: len(unit.indices))
        self.assertEqual(result.value, 2.0)

    def test_nan_is_rejected(self):
        energy = StructuralEnergy(lambda p: float("nan"))
        with self.assertRaises(ValueError):
            energy(self.partition())


if __name__ == "__main__":
    unittest.main()
