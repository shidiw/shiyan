import unittest

from structure.theory_representation import represent
from structure.theory_world import StructuralWorld


class TestTheoryRepresentationInvarianceContract(unittest.TestCase):
    def test_representation_does_not_claim_invariance_for_arbitrary_extractor(self):
        world = StructuralWorld(units=tuple(), relations=tuple())

        def extractor(w):
            return [float(w.unit_count)] * 23

        representation = represent(world, extractor)
        self.assertEqual(len(representation.values), 23)
        self.assertEqual(representation.values[0], 0.0)

    def test_extractor_is_the_only_source_of_numeric_coordinates(self):
        world = StructuralWorld(units=tuple(), relations=tuple())

        calls = []

        def extractor(w):
            calls.append(w)
            return [1.0] * 23

        representation = represent(world, extractor)
        self.assertEqual(len(calls), 1)
        self.assertEqual(representation.values, (1.0,) * 23)


if __name__ == "__main__":
    unittest.main()
