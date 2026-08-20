import unittest

from structure.theory_stability import (
    StabilityNeighborhood,
    is_locally_stable,
    is_minimal_stable,
)


class TestTheoryStability(unittest.TestCase):
    def test_stability_requires_no_lower_energy_alternative(self):
        self.assertTrue(
            is_locally_stable(
                "a",
                StabilityNeighborhood(("b", "c")),
                lambda x: {"a": 1.0, "b": 1.0, "c": 2.0}[x],
            )
        )
        self.assertFalse(
            is_locally_stable(
                "a",
                StabilityNeighborhood(("b", "c")),
                lambda x: {"a": 1.0, "b": 0.5, "c": 2.0}[x],
            )
        )

    def test_empty_neighborhood_is_rejected(self):
        with self.assertRaises(ValueError):
            StabilityNeighborhood(())

    def test_nonfinite_energy_is_rejected(self):
        with self.assertRaises(ValueError):
            is_locally_stable(
                "a",
                StabilityNeighborhood(("b",)),
                lambda x: float("nan"),
            )

    def test_minimal_stable_rejects_stable_proper_subcandidate(self):
        energies = {"A": 1.0, "B": 1.0, "C": 2.0}
        neighborhoods = {
            "A": StabilityNeighborhood(("C",)),
            "B": StabilityNeighborhood(("A",)),
            "C": StabilityNeighborhood(("A",)),
        }
        self.assertFalse(
            is_minimal_stable(
                "A",
                lambda x: neighborhoods[x],
                ("B",),
                lambda x: energies[x],
            )
        )

    def test_minimal_stable_accepts_no_stable_proper_subcandidate(self):
        energies = {"A": 1.0, "B": 2.0}
        neighborhoods = {
            "A": StabilityNeighborhood(("B",)),
            "B": StabilityNeighborhood(("A",)),
        }
        self.assertTrue(
            is_minimal_stable(
                "A",
                lambda x: neighborhoods[x],
                ("B",),
                lambda x: energies[x],
            )
        )

    def test_stability_is_an_explicit_input_boundary(self):
        neighborhoods = StabilityNeighborhood(("b",))
        self.assertEqual(neighborhoods.alternatives, ("b",))


if __name__ == "__main__":
    unittest.main()
