import unittest

from structure.theory_core import Partition, StructuralUnit, TheoryUnit
from structure.theory_energy_model import Observation3D
from structure.theory_invariant import invariant_equal, structural_invariant
from structure.theory_materialization import materialize_units
from structure.theory_relation import StructuralRelation
from structure.theory_unit_invariant import (
    Can_U,
    can_u_is_invariant_under_relabeling,
    relabel_unit,
    unit_equivalent_X,
)
from structure.theory_world import StructuralWorld


class TestTheoryUnitBoundary(unittest.TestCase):
    def test_theory_unit_is_single_structural_unit_type(self):
        self.assertIs(TheoryUnit, StructuralUnit)

    def test_primitive_is_optional_metadata(self):
        unit = StructuralUnit((0, 1), attributes={"curvature": 0.2})
        self.assertEqual(unit.support, (0, 1))
        self.assertEqual(unit.theta["curvature"], 0.2)
        self.assertIsNone(unit.primitive)

    def test_materialization_is_identity_on_partition_cells(self):
        units = (StructuralUnit((0,), {}), StructuralUnit((1,), {}))
        partition = Partition(units, (0, 1))
        self.assertEqual(materialize_units(partition), units)

    def test_legacy_positional_constructor_materializes_same_unit(self):
        canonical = StructuralUnit((0, 1), {"kind": "candidate"}, None)
        legacy = TheoryUnit((0, 1), "candidate", {})
        self.assertEqual(legacy.indices, canonical.indices)
        self.assertEqual(legacy.attributes, canonical.attributes)
        self.assertEqual(legacy.primitive, "candidate")


class TestTheoryInvariantStage(unittest.TestCase):
    def _world_pair(self):
        a = StructuralWorld(
            units=(
                StructuralUnit((0,), {"kind": "a"}),
                StructuralUnit((1,), {"kind": "b"}),
            ),
            relations=(StructuralRelation(0, 1, "adjacent"),),
        )
        b = StructuralWorld(
            units=(
                StructuralUnit((1,), {"kind": "b"}),
                StructuralUnit((0,), {"kind": "a"}),
            ),
            relations=(StructuralRelation(1, 0, "adjacent"),),
        )
        return a, b

    def test_invariant_is_deterministic(self):
        a, _ = self._world_pair()
        self.assertEqual(structural_invariant(a), structural_invariant(a))

    def test_invariant_is_relabeling_invariant(self):
        a, b = self._world_pair()
        self.assertEqual(structural_invariant(a), structural_invariant(b))
        self.assertTrue(invariant_equal(a, b))


class TestCompleteObservationUnitInvariant(unittest.TestCase):
    def setUp(self):
        self.observation = Observation3D(
            (
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (0.0, 1.0, 0.0),
                (0.0, 0.0, 1.0),
            )
        )

    def test_current_index_tuple_is_not_complete_under_relabeling(self):
        first = StructuralUnit((0, 1), {"role": "surface"})
        second = StructuralUnit((2, 3), {"role": "surface"})
        self.assertNotEqual(first.indices, second.indices)
        relabeled = Observation3D((
            self.observation.points[2],
            self.observation.points[3],
            self.observation.points[0],
            self.observation.points[1],
        ))
        transported = StructuralUnit((2, 3), {"role": "surface"})
        self.assertTrue(unit_equivalent_X(first, transported, relabeled))

    def test_can_u_is_invariant_under_observation_relabeling(self):
        unit = StructuralUnit((0, 2), {"role": "surface"})
        permutation = (2, 0, 3, 1)
        self.assertTrue(can_u_is_invariant_under_relabeling(unit, self.observation, permutation))

    def test_can_u_is_complete_for_frozen_unit_quotient(self):
        first = StructuralUnit((0, 2), {"role": "surface"})
        relabeled_observation = Observation3D((
            self.observation.points[1],
            self.observation.points[0],
            self.observation.points[3],
            self.observation.points[2],
        ))
        second = StructuralUnit((1, 3), {"role": "surface"})
        self.assertTrue(unit_equivalent_X(first, second, relabeled_observation))
        self.assertEqual(Can_U(first, self.observation), Can_U(second, relabeled_observation))

    def test_different_geometry_is_not_identified(self):
        first = StructuralUnit((0, 1), {})
        second = StructuralUnit((0, 2), {})
        self.assertNotEqual(Can_U(first, self.observation), Can_U(second, self.observation))
        self.assertFalse(unit_equivalent_X(first, second, self.observation))

    def test_different_theta_is_not_identified(self):
        first = StructuralUnit((0, 1), {"role": "a"})
        second = StructuralUnit((0, 1), {"role": "b"})
        self.assertNotEqual(Can_U(first, self.observation), Can_U(second, self.observation))
        self.assertFalse(unit_equivalent_X(first, second, self.observation))

    def test_primitive_metadata_is_not_part_of_frozen_unit_identity(self):
        first = StructuralUnit((0, 1), {"role": "surface"}, "plane")
        second = StructuralUnit((0, 1), {"role": "surface"}, "legacy-label")
        self.assertEqual(Can_U(first, self.observation), Can_U(second, self.observation))
        self.assertTrue(unit_equivalent_X(first, second, self.observation))

    def test_relabel_transport_uses_inverse_permutation(self):
        unit = StructuralUnit((0, 2), {})
        permutation = (2, 0, 3, 1)
        transported = relabel_unit(unit, permutation)
        self.assertEqual(transported.indices, (1, 2))

    def test_can_u_is_finite_and_hashable(self):
        unit = StructuralUnit((0, 1, 3), {"weight": [1, 2, 3]})
        invariant = Can_U(unit, self.observation)
        self.assertIsInstance(invariant, tuple)
        hash(invariant)


if __name__ == "__main__":
    unittest.main()
