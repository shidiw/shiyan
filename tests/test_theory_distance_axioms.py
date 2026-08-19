import unittest

from structure.theory_distance import structural_distance
from structure.theory_representation import REPRESENTATION_DIM, StructuralRepresentation


class TestTheoryDistanceAxioms(unittest.TestCase):
    def rep(self, values):
        return StructuralRepresentation(tuple(float(v) for v in values))

    def test_non_negativity(self):
        a = self.rep([0.0] * REPRESENTATION_DIM)
        b = self.rep([1.0] * REPRESENTATION_DIM)
        self.assertGreaterEqual(structural_distance(a, b), 0.0)

    def test_symmetry(self):
        a = self.rep([0.0] * REPRESENTATION_DIM)
        b = self.rep([1.0] + [0.0] * (REPRESENTATION_DIM - 1))
        self.assertEqual(structural_distance(a, b), structural_distance(b, a))

    def test_triangle_inequality(self):
        a = self.rep([0.0] * REPRESENTATION_DIM)
        b = self.rep([1.0] + [0.0] * (REPRESENTATION_DIM - 1))
        c = self.rep([1.0, 1.0] + [0.0] * (REPRESENTATION_DIM - 2))
        dab = structural_distance(a, b)
        dbc = structural_distance(b, c)
        dac = structural_distance(a, c)
        self.assertLessEqual(dac, dab + dbc + 1e-12)

    def test_zero_distance_is_representation_equality(self):
        a = self.rep([0.0] * REPRESENTATION_DIM)
        b = self.rep([0.0] * REPRESENTATION_DIM)
        self.assertEqual(structural_distance(a, b), 0.0)


if __name__ == "__main__":
    unittest.main()
