import unittest

from structure.theory_stage2 import DERIVED, FROZEN_THEORY, THEORY_GAP, stage2_status


class TestTheoryStage2Boundary(unittest.TestCase):
    def test_frozen_core_concepts_are_explicit(self):
        for concept in ("Unit", "Relation", "Graph", "World"):
            self.assertEqual(stage2_status(concept).status, FROZEN_THEORY)

    def test_object_is_derived_not_frozen_theorem(self):
        self.assertEqual(stage2_status("Object").status, DERIVED)

    def test_instance_and_hierarchy_are_not_promoted_without_definition(self):
        self.assertEqual(stage2_status("Instance").status, THEORY_GAP)
        self.assertEqual(stage2_status("Hierarchy").status, THEORY_GAP)

    def test_unknown_concept_is_rejected(self):
        with self.assertRaises(KeyError):
            stage2_status("InventedLayer")


if __name__ == "__main__":
    unittest.main()
