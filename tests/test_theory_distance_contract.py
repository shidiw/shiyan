import unittest

from structure.theory_distance import structural_distance
from structure.theory_representation import StructuralRepresentation


class TestTheoryDistanceContract(unittest.TestCase):
    def test_zero_distance_is_exactly_equal_representation(self):
        a = StructuralRepresentation((1.0,) * 23)
        b = StructuralRepresentation((1.0,) * 23)
        self.assertEqual(structural_distance(a, b), 0.0)

    def test_distance_does_not_claim_structural_identity(self):
        # Two worlds can share the same frozen representation without the
        # current theory proving that they are structurally isomorphic.
        a = StructuralRepresentation((0.0,) * 23)
        b = StructuralRepresentation((0.0,) * 23)
        self.assertEqual(structural_distance(a, b), 0.0)


if __name__ == "__main__":
    unittest.main()
