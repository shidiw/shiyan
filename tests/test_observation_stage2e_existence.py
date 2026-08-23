import unittest

from structure.theory_observation import ObservationDerivedContext
from structure.theory_stage2e_existence import (
    derived_unit_energy_margin,
    observation_unit_family_is_complete,
    prove_observation_derived_stage2e_existence,
)


class TestObservationDerivedStage2EExistence(unittest.TestCase):
    def setUp(self):
        self.context = ObservationDerivedContext.from_points(
            (
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (0.0, 1.0, 0.0),
            )
        )

    def test_unit_family_is_complete_nonempty_support_lattice(self):
        self.assertTrue(observation_unit_family_is_complete(self.context))
        self.assertEqual(len(self.context.unit_candidates), 7)

    def test_stage2e_existence_is_observation_derived(self):
        result = prove_observation_derived_stage2e_existence(self.context)
        self.assertTrue(result.materializable)
        self.assertTrue(result.candidate_count > 0)
        self.assertTrue(result.stable_unit_count > 0)
        self.assertEqual(len(result.unit.indices), 1)

    def test_minimum_support_stable_witness_has_no_stable_frozen_subcandidate(self):
        result = prove_observation_derived_stage2e_existence(self.context)
        stable = []
        energy = self.context.stage2d_energy().unit_energy
        for unit in self.context.unit_candidates:
            if self.context.neighborhood_rule(unit).alternatives:
                from structure.theory_stability import is_locally_stable
                if is_locally_stable(unit, self.context.neighborhood_rule(unit), energy):
                    stable.append(unit)
        self.assertEqual(len(result.unit.indices), min(len(u.indices) for u in stable))

    def test_derived_unit_margin_is_not_an_external_input(self):
        energy = self.context.stage2d_energy().unit_energy
        margin = derived_unit_energy_margin(self.context.unit_candidates, energy)
        self.assertGreaterEqual(margin, 0.0)
        self.assertEqual(
            margin,
            prove_observation_derived_stage2e_existence(self.context).derived_unit_margin,
        )

    def test_strict_margin_is_conditional_on_derived_gap(self):
        result = prove_observation_derived_stage2e_existence(self.context)
        if result.strict_margin_available:
            strict = prove_observation_derived_stage2e_existence(
                self.context, require_strict_margin=True
            )
            self.assertTrue(strict.materializable)
        else:
            with self.assertRaises(ValueError):
                prove_observation_derived_stage2e_existence(
                    self.context, require_strict_margin=True
                )


if __name__ == "__main__":
    unittest.main()
