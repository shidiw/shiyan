import unittest

from structure.theory_distance import structural_distance
from structure.theory_matching import select_matching
from structure.theory_neural import (
    combined_loss,
    distance_preservation_loss,
    mutation_consistency_loss,
    reconstruction_loss,
)
from structure.theory_representation import REPRESENTATION_DIM, StructuralRepresentation


class TestTheoryRepresentationDistance(unittest.TestCase):
    def rep(self, value):
        return StructuralRepresentation(tuple([float(value)] * REPRESENTATION_DIM))

    def test_representation_dimension_is_frozen_at_23(self):
        self.assertEqual(len(self.rep(0).values), 23)
        with self.assertRaises(ValueError):
            StructuralRepresentation((0.0,) * 22)

    def test_distance_is_euclidean(self):
        self.assertAlmostEqual(structural_distance(self.rep(0), self.rep(1)), 23 ** 0.5)
        self.assertEqual(structural_distance(self.rep(2), self.rep(2)), 0.0)
        self.assertEqual(structural_distance(self.rep(0), self.rep(1)), structural_distance(self.rep(1), self.rep(0)))

    def test_matching_selects_minimum(self):
        result = select_matching(
            (((0, 0),), ((0, 1),)),
            lambda pairs: 2.0 if pairs[0][1] == 0 else 0.5,
        )
        self.assertEqual(result.pairs, ((0, 1),))
        self.assertEqual(result.cost, 0.5)

    def test_neural_losses(self):
        self.assertEqual(reconstruction_loss((1, 2), (1, 2)), 0.0)
        self.assertGreater(distance_preservation_loss((0,), (2,), 1.0), 0.0)
        self.assertEqual(mutation_consistency_loss(0.0, 1.0), 1.0)
        self.assertEqual(mutation_consistency_loss(1.0, 1.0), 0.0)
        # L = L_recon + lambda_d * L_distance + lambda_m * L_mutation.
        # 1 + 0.5*2 + 0.25*3 = 2.75.
        self.assertEqual(combined_loss(1, 2, 3, 0.5, 0.25), 2.75)


if __name__ == "__main__":
    unittest.main()
