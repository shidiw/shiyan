import unittest

from structure.theory_representation import represent
from structure.theory_world import StructuralWorld


class TestTheoryWorldPhiBoundary(unittest.TestCase):
    def test_world_phi_is_explicitly_supplied(self):
        world = StructuralWorld(units=tuple(), relations=tuple())
        self.assertEqual(represent(world, lambda _: [0.0] * 23).as_tuple(), (0.0,) * 23)

    def test_world_attributes_are_not_silently_promoted_to_phi(self):
        world = StructuralWorld(
            units=tuple(),
            relations=tuple(),
            attributes={"primitive_histogram": [9.0, 9.0, 9.0]},
        )
        self.assertEqual(represent(world, lambda _: [0.0] * 23).as_tuple(), (0.0,) * 23)


if __name__ == "__main__":
    unittest.main()
