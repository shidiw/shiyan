import unittest
from pathlib import Path


class TestGlobalClosureAuditContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = Path(__file__).resolve().parents[1] / "docs" / "STRUCT3D_GLOBAL_CLOSURE_AUDIT.md"
        cls.text = cls.path.read_text(encoding="utf-8")

    def test_global_audit_exists_and_keeps_open_links_explicit(self):
        text = self.text
        for marker in (
            "X -> A(X)",
            "MinimalStable -> Unit",
            "Invariant -> phi in R^23",
            "Universal relation construction",
            "Neural distance preservation",
        ):
            self.assertIn(marker, text)

    def test_formal_observation_interface_is_frozen(self):
        text = self.text
        self.assertIn("ObservationDerivedTheoryInterface", text)
        self.assertIn("ObservationDerivedBoundaries.from_points(X)", text)
        self.assertIn("No constructor argument exists for any former external boundary", text)
        self.assertIn("test_observation_derived_formal_interface.py", text)

    def test_derived_extensions_are_not_mislabeled_as_recovered_history(self):
        text = self.text
        self.assertIn("DERIVED EXTENSION", text)
        self.assertIn("mathematically explicit extension, not a historical recovery", text)
        self.assertIn("legacy `structure/energy.py` remains regression-only", text)

    def test_engineering_corrections_are_recorded(self):
        text = self.text
        self.assertIn("rejects `NaN` **and** positive/negative infinity", text)
        self.assertIn("negative observation indices", text)
        self.assertIn("duplicate ordered edges", text)
        self.assertIn("finite real values", text)


if __name__ == "__main__":
    unittest.main()
