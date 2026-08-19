import unittest
from pathlib import Path


class TestMathCodeMapContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = Path(__file__).resolve().parents[1] / "docs" / "STRUCT3D_MATH_CODE_MAP.md"
        cls.text = cls.path.read_text(encoding="utf-8")

    def test_release_contract_exists_and_marks_theory_gaps_explicitly(self):
        text = self.text
        self.assertIn("Structural Unit", text)
        self.assertIn("single frozen Unit type", text)
        self.assertIn("Structural invariant `I(W)=C(W)`", text)
        self.assertIn("Representation distance", text)
        self.assertIn("Theory gap; intentionally not implemented", text)
        self.assertIn("Legacy `structure/energy.py`", text)

    def test_full_version_chain_is_audited(self):
        text = self.text
        for stage in ("v0.0", "v0.1", "v0.2", "v0.3", "v0.4", "v0.5",
                      "v0.6", "v0.7", "v0.8", "v0.9", "v1.0", "v2.x",
                      "v3.6", "v3.7", "v3.8", "v3.9", "v4.0"):
            self.assertIn(stage, text, msg=f"missing theory/code audit stage: {stage}")

    def test_unfrozen_layers_are_explicitly_blocked(self):
        text = self.text
        self.assertIn("Instance", text)
        self.assertIn("Hierarchy", text)
        self.assertIn("must not be promoted into the frozen theory", text)

    def test_contract_does_not_promote_neural_metric_equality(self):
        text = self.text
        self.assertIn("must not be reported as a proof", text)
        self.assertIn("D_R=0", text)


if __name__ == "__main__":
    unittest.main()
