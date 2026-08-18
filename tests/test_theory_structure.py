import unittest

from structure.theory_canonical import canonical_form, structurally_equivalent
from structure.theory_core import TheoryUnit
from structure.theory_object import assemble_objects
from structure.theory_relation import StructuralRelation
from structure.theory_world import StructuralWorld


class TestTheoryStructure(unittest.TestCase):
    def units(self):
        return (
            TheoryUnit((0,), attributes={"shape": "a"}),
            TheoryUnit((1,), attributes={"shape": "b"}),
            TheoryUnit((2,), attributes={"shape": "c"}),
        )

    def test_relation_is_not_derived_from_primitive_equality(self):
        relation = StructuralRelation(0, 1, "assembly", {"geometry": 1.0})
        self.assertEqual(relation.units, (0, 1))

    def test_world_validates_relation_domain(self):
        with self.assertRaises(ValueError):
            StructuralWorld(self.units(), (StructuralRelation(0, 3, "assembly"),))

    def test_assembly_uses_only_explicit_assembly_relations(self):
        rels = (
            StructuralRelation(0, 1, "near"),
            StructuralRelation(1, 2, "assembly"),
        )
        objects = assemble_objects(self.units(), rels)
        self.assertEqual(tuple(o.unit_ids for o in objects), ((0,), (1, 2)))

    def test_canonical_form_is_relabeling_invariant(self):
        u = self.units()
        w1 = StructuralWorld(
            u,
            (StructuralRelation(0, 1, "assembly"), StructuralRelation(1, 2, "near")),
        )
        w2 = StructuralWorld(
            (u[2], u[0], u[1]),
            (StructuralRelation(1, 2, "assembly"), StructuralRelation(2, 0, "near")),
        )
        self.assertEqual(canonical_form(w1), canonical_form(w2))
        self.assertTrue(structurally_equivalent(w1, w2))


if __name__ == "__main__":
    unittest.main()
