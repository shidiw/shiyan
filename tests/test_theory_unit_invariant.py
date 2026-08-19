import unittest

from structure.theory_core import Partition, StructuralUnit, TheoryUnit
from structure.theory_invariant import invariant_equal, structural_invariant
from structure.theory_materialization import materialize_units
from structure.theory_relation import StructuralRelation
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


if __name__ == "__main__":
    unittest.main()
