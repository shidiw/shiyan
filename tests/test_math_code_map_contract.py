import unittest
from pathlib import Path


class TestMathCodeMapContract(unittest.TestCase):
    def test_release_contract_exists_and_marks_theory_gaps_explicitly(self):
        path = Path(__file__).resolve().parents[1] / "docs" / "STRUCT3D_MATH_CODE_MAP.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn("Structural Unit", text)
        self.assertIn("single Unit type", text)
        self.assertIn("Structural invariant `I(W)=C(W)`", text)
        self.assertIn("Representation distance", text)
        self.assertIn("Theory gap; intentionally not implemented", text)
        self.assertIn("Legacy `structure/energy.py`", text)

    def test_contract_does_not_promote_neural_metric_equality(self):
        path = Path(__file__).resolve().parents[1] / "docs" / "STRUCT3D_MATH_CODE_MAP.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn("must not be reported as a proof", text)
        self.assertIn("D_R=0", text)


if __name__ == "__main__":
    unittest.main()
