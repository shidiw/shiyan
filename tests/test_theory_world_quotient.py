import unittest

from structure.theory_observation_theta import observation_unit
from structure.theory_relation import StructuralRelation
from structure.theory_world import StructuralWorld
from structure.theory_world_quotient import (
    phi_well_defined_on_quotient,
    prove_structural_world_quotient,
    quotient_representation,
    world_quotient_equivalent,
    world_quotient_form,
)
from structure.theory_energy_model import Observation3D


class TestStructuralWorldQuotient(unittest.TestCase):
    def setUp(self):
        self.X = Observation3D(
            points=(
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (0.0, 2.0, 0.0),
            )
        )
        self.u0 = observation_unit(self.X, (0,))
        self.u1 = observation_unit(self.X, (1, 2))

    def _world(self):
        return StructuralWorld(
            units=(self.u0, self.u1),
            relations=(StructuralRelation(0, 1, "adjacent", {"rule": "explicit"}),),
        )

    def _relabelled_world(self):
        # old -> new observation indices
        permutation = {0: 2, 1: 0, 2: 1}
        relabeled_points = [None] * 3
        for old, new in permutation.items():
            relabeled_points[new] = self.X.points[old]
        Xp = Observation3D(points=tuple(relabeled_points))

        # Keep the same Unit order at the world level; only raw support indices
        # change. The explicit relation remains 0 -> 1.
        v0 = observation_unit(Xp, (2,))
        v1 = observation_unit(Xp, (0, 1))
        return StructuralWorld(
            units=(v0, v1),
            relations=(StructuralRelation(0, 1, "adjacent", {"rule": "explicit"}),),
        )

    def test_world_quotient_equivalence_is_index_free(self):
        a = self._world()
        b = self._relabelled_world()
        self.assertTrue(world_quotient_equivalent(a, b))
        self.assertEqual(world_quotient_form(a), world_quotient_form(b))

    def test_structural_world_quotient_theorem_certificate(self):
        self.assertTrue(prove_structural_world_quotient(self._world(), self._relabelled_world()))

    def test_bad_raw_phi_is_detected(self):
        worlds = (self._world(), self._relabelled_world())

        def bad_phi(world):
            return [float(world.units[0].indices[0])] * 23

        self.assertFalse(phi_well_defined_on_quotient(worlds, bad_phi))

    def test_quotient_phi_is_well_defined_by_construction(self):
        worlds = (self._world(), self._relabelled_world())

        def extractor(canonical):
            return [float(len(canonical[0])), float(len(canonical[1]))] + [0.0] * 21

        self.assertEqual(
            quotient_representation(worlds[0], extractor),
            quotient_representation(worlds[1], extractor),
        )

    def test_good_raw_phi_passes_finite_audit(self):
        worlds = (self._world(), self._relabelled_world())

        def good_phi(world):
            return [float(len(world.units)), float(len(world.relations))] + [0.0] * 21

        self.assertTrue(phi_well_defined_on_quotient(worlds, good_phi))


if __name__ == "__main__":
    unittest.main()
