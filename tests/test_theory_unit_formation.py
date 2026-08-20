import unittest

from structure.theory_stability import StabilityNeighborhood
from structure.theory_unit import StructuralUnit
from structure.theory_unit_formation import (
    evaluate_unit_formation,
    materialize_unit,
)


class TestTheoryUnitFormation(unittest.TestCase):
    def setUp(self):
        self.a = StructuralUnit((0, 1), {})
        self.b = StructuralUnit((0,), {})
        self.c = StructuralUnit((1,), {})

    def test_stable_minimal_candidate_is_materializable(self):
        energies = {self.a: 1.0, self.b: 2.0, self.c: 2.0}
        neighborhoods = {
            self.a: StabilityNeighborhood((self.b, self.c)),
            self.b: StabilityNeighborhood((self.a,)),
            self.c: StabilityNeighborhood((self.a,)),
        }
        result = evaluate_unit_formation(
            self.a,
            lambda unit: neighborhoods[unit],
            (self.b, self.c),
            lambda unit: energies[unit],
        )
        self.assertTrue(result.stable)
        self.assertTrue(result.minimal_stable)
        self.assertTrue(result.materializable)
        self.assertEqual(materialize_unit(
            self.a,
            lambda unit: neighborhoods[unit],
            (self.b, self.c),
            lambda unit: energies[unit],
        ), self.a)

    def test_lower_energy_alternative_blocks_materialization(self):
        energies = {self.a: 1.0, self.b: 0.5, self.c: 2.0}
        neighborhoods = {self.a: StabilityNeighborhood((self.b, self.c))}
        result = evaluate_unit_formation(
            self.a,
            lambda unit: neighborhoods[unit],
            (),
            lambda unit: energies[unit],
        )
        self.assertFalse(result.stable)
        self.assertFalse(result.materializable)
        with self.assertRaises(ValueError):
            materialize_unit(
                self.a,
                lambda unit: neighborhoods[unit],
                (),
                lambda unit: energies[unit],
            )

    def test_stable_proper_subcandidate_blocks_minimality(self):
        energies = {self.a: 1.0, self.b: 1.0, self.c: 2.0}
        neighborhoods = {
            self.a: StabilityNeighborhood((self.c,)),
            self.b: StabilityNeighborhood((self.c,)),
            self.c: StabilityNeighborhood((self.a,)),
        }
        result = evaluate_unit_formation(
            self.a,
            lambda unit: neighborhoods[unit],
            (self.b,),
            lambda unit: energies[unit],
        )
        self.assertTrue(result.stable)
        self.assertFalse(result.minimal_stable)
        self.assertFalse(result.materializable)

    def test_formation_does_not_infer_neighborhood(self):
        neighborhood = StabilityNeighborhood((self.b,))
        result = evaluate_unit_formation(
            self.a,
            lambda unit: neighborhood,
            (),
            lambda unit: 1.0,
        )
        self.assertTrue(result.stable)

    def test_no_unique_optimum_is_claimed_on_equal_energy(self):
        energies = {self.a: 1.0, self.b: 1.0}
        neighborhoods = {
            self.a: StabilityNeighborhood((self.b,)),
            self.b: StabilityNeighborhood((self.a,)),
        }
        result = evaluate_unit_formation(
            self.a,
            lambda unit: neighborhoods[unit],
            (),
            lambda unit: energies[unit],
        )
        self.assertTrue(result.stable)
        self.assertTrue(result.minimal_stable)


if __name__ == "__main__":
    unittest.main()
