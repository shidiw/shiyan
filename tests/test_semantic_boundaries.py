import unittest

from structure.theory_candidate_search import A_search, is_subset_of_A_max
from structure.theory_observation import ObservationDerivedContext
from structure.theory_semantic_observation import M_X, Q_X, Q_X_strength


class TestSemanticBoundaryStrength(unittest.TestCase):
    def setUp(self):
        self.points = (
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (5.0, 5.0, 5.0),
        )
        self.context = ObservationDerivedContext.from_points(self.points)

    def test_M_X_is_finite_nonempty_and_subset_of_M(self):
        for unit in self.context.unit_candidates:
            selected = M_X(unit, self.context)
            self.assertTrue(selected)
            self.assertTrue(set(selected).issubset(set(self.context.model_family)))

    def test_M_X_is_an_argmin_of_the_local_regularized_score(self):
        unit = self.context.unit_candidates[-1]
        selected = M_X(unit, self.context)
        selected_names = {model.name for model in selected}
        self.assertTrue(selected_names)
        scores = []
        for model in self.context.model_family:
            residual = sum(
                model.squared_distance(self.context.observation.points[i])
                for i in unit.indices
            )
            score = residual / (len(unit.indices) * self.context.observation.scale ** 2) + model.complexity
            scores.append((model.name, score))
        minimum = min(score for _, score in scores)
        self.assertEqual(
            selected_names,
            {name for name, score in scores if score == minimum},
        )

    def test_Q_X_is_stronger_than_positive_confidence(self):
        near_a = self.context.unit_candidates[0]
        near_b = self.context.unit_candidates[1]
        far_a = self.context.unit_candidates[0]
        far_b = self.context.unit_candidates[-1]
        self.assertTrue(Q_X(near_a, near_b, self.context))
        self.assertGreaterEqual(Q_X_strength(near_a, near_b, self.context), 0.0)
        self.assertLessEqual(Q_X_strength(near_a, near_b, self.context), 1.0)
        self.assertFalse(Q_X(far_a, far_b, self.context) and Q_X_strength(far_a, far_b, self.context) <= 0.0)

    def test_Q_X_is_relabeling_compatible(self):
        permutation = (3, 1, 0, 2)
        relabeled = tuple(self.points[i] for i in permutation)
        other = ObservationDerivedContext.from_points(relabeled)
        a = self.context.unit_candidates[0]
        b = self.context.unit_candidates[1]
        mapped_a = type(a)(tuple(permutation.index(i) for i in a.indices), dict(a.attributes))
        mapped_b = type(b)(tuple(permutation.index(i) for i in b.indices), dict(b.attributes))
        self.assertEqual(Q_X(a, b, self.context), Q_X(mapped_a, mapped_b, other))

    def test_A_search_is_finite_nonempty_and_proper_for_nontrivial_X(self):
        blocks = A_search(self.context.observation)
        self.assertTrue(blocks)
        self.assertTrue(is_subset_of_A_max(self.context.observation, blocks))
        self.assertLess(len(blocks), len(self.context.a_max))

    def test_A_search_is_relabeling_compatible_in_cardinality(self):
        blocks = A_search(self.context.observation)
        relabeled = tuple(self.points[i] for i in (2, 0, 3, 1))
        other = ObservationDerivedContext.from_points(relabeled)
        self.assertEqual(len(blocks), len(A_search(other.observation)))


if __name__ == "__main__":
    unittest.main()
