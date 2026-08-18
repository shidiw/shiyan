import unittest

from structure.theory_neural_objective import NeuralObjective, combine_losses


class TestTheoryNeuralObjective(unittest.TestCase):
    def test_reconstruction_only_is_explicit_default(self):
        objective = NeuralObjective()
        self.assertEqual(combine_losses(2.0, 7.0, 11.0, objective), 2.0)

    def test_all_terms_use_explicit_weights(self):
        objective = NeuralObjective(1.0, 0.5, 0.25)
        self.assertEqual(combine_losses(1.0, 2.0, 4.0, objective), 3.0)

    def test_negative_weight_is_rejected(self):
        with self.assertRaises(ValueError):
            NeuralObjective(distance_weight=-1.0)

    def test_nan_loss_is_rejected(self):
        with self.assertRaises(ValueError):
            combine_losses(float("nan"), 0.0, 0.0, NeuralObjective())


if __name__ == "__main__":
    unittest.main()
