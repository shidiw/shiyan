import unittest

from structure.theory_matching import select_matching


class TestTheoryMatchingContract(unittest.TestCase):
    def test_matching_is_argmin_over_supplied_admissible_set(self):
        candidates = (((0, 0),), ((0, 1),), ((1, 0),))
        result = select_matching(candidates, lambda p: {((0, 0),): 3.0, ((0, 1),): 1.0, ((1, 0),): 2.0}[p])
        self.assertEqual(result.pairs, ((0, 1),))
        self.assertEqual(result.cost, 1.0)

    def test_empty_admissible_set_is_not_a_matching_problem(self):
        with self.assertRaises(ValueError):
            select_matching([], lambda _: 0.0)

    def test_matching_does_not_claim_unique_optimum_on_tie(self):
        candidates = (((0, 0),), ((1, 1),))
        result = select_matching(candidates, lambda _: 1.0)
        self.assertIn(result.pairs, candidates)
        self.assertEqual(result.cost, 1.0)


if __name__ == "__main__":
    unittest.main()
