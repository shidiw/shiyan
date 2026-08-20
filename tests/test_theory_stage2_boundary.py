import unittest

from structure.theory_stage2 import (
    CONDITIONAL_THEOREM,
    DERIVED,
    EXPLICIT_BOUNDARY,
    FROZEN_THEORY,
    THEORY_GAP,
    stage2_status,
)


class TestTheoryStage2Boundary(unittest.TestCase):
    def test_frozen_core_concepts_are_explicit(self):
        for concept in ("Unit", "Relation", "Graph", "World"):
            self.assertEqual(stage2_status(concept).status, FROZEN_THEORY)

    def test_upstream_closure_objects_are_explicit_boundaries(self):
        for concept in ("CandidateFamily", "Energy", "Stability", "Minimality"):
            self.assertEqual(stage2_status(concept).status, EXPLICIT_BOUNDARY)

    def test_existence_is_a_conditional_theorem(self):
        status = stage2_status("Existence")
        self.assertEqual(status.status, CONDITIONAL_THEOREM)
        self.assertIn("non-empty finite A(X)", status.mathematical_definition)
        self.assertIn("attained argmin", status.mathematical_definition)

    def test_uniqueness_is_a_conditional_theorem(self):
        status = stage2_status("Uniqueness")
        self.assertEqual(status.status, CONDITIONAL_THEOREM)
        self.assertIn("strictly lower", status.mathematical_definition)
        self.assertIn("unique argmin", status.mathematical_definition)

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
