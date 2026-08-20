import unittest

from structure.theory_unit import StructuralUnit
from structure.theory_unit_emergence import (
    ObservationDomain,
    admissible_candidates,
    emergent_units,
    materialize_emergent_unit,
    stable_candidates,
)


class TestTheoryUnitEmergence(unittest.TestCase):
    def test_admissible_family_is_all_nonempty_subsets(self):
        domain = ObservationDomain((0, 1, 2))
        family = admissible_candidates(domain)
        self.assertEqual(len(family), 7)
        self.assertEqual(
            {unit.indices for unit in family},
            {
                (0,), (1,), (2,),
                (0, 1), (0, 2), (1, 2),
                (0, 1, 2),
            },
        )

    def test_finite_energy_has_stable_candidate(self):
        domain = ObservationDomain((0, 1))
        energies = {
            (0,): 2.0,
            (1,): 3.0,
            (0, 1): 1.0,
        }
        stable = stable_candidates(domain, lambda unit: energies[unit.indices])
        self.assertEqual(tuple(unit.indices for unit in stable), ((0, 1),))

    def test_equal_global_minima_remain_set_valued(self):
        domain = ObservationDomain((0, 1))
        energies = {
            (0,): 1.0,
            (1,): 1.0,
            (0, 1): 2.0,
        }
        stable = stable_candidates(domain, lambda unit: energies[unit.indices])
        self.assertEqual({unit.indices for unit in stable}, {(0,), (1,)})
        emerged = emergent_units(domain, lambda unit: energies[unit.indices])
        self.assertEqual({unit.indices for unit in emerged}, {(0,), (1,)})

    def test_strict_minimum_materializes(self):
        domain = ObservationDomain((0, 1))
        energies = {
            (0,): 2.0,
            (1,): 2.0,
            (0, 1): 1.0,
        }
        result = materialize_emergent_unit(
            domain,
            lambda candidate: energies[candidate.indices],
        )
        self.assertEqual(result, StructuralUnit((0, 1), {}))

    def test_nonfinite_energy_is_rejected(self):
        domain = ObservationDomain((0, 1))
        with self.assertRaises(ValueError):
            stable_candidates(domain, lambda unit: float("inf"))

    def test_domain_is_nonempty_and_unique(self):
        with self.assertRaises(ValueError):
            ObservationDomain(())
        with self.assertRaises(ValueError):
            ObservationDomain((0, 0))


if __name__ == "__main__":
    unittest.main()
