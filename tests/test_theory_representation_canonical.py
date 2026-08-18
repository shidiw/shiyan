import unittest

from structure.theory_representation import represent, represent_canonical
from structure.theory_unit import StructuralUnit
from structure.theory_world import StructuralWorld
from structure.theory_relation import StructuralRelation


class TestTheoryRepresentationCanonical(unittest.TestCase):
    def _world_pair(self):
        units = (
            StructuralUnit(indices=(0,), primitive="plane"),
            StructuralUnit(indices=(1,), primitive="sphere"),
        )
        a = StructuralWorld(
            units=units,
            relations=(StructuralRelation(0, 1, "adjacent"),),
        )
        b = StructuralWorld(
            units=(units[1], units[0]),
            relations=(StructuralRelation(1, 0, "adjacent"),),
        )
        return a, b

    def test_world_extractor_is_not_claimed_invariant(self):
        a, b = self._world_pair()

        def extractor(world):
            return [float(world.units[0].indices[0])] * 23

        self.assertNotEqual(represent(a, extractor), represent(b, extractor))

    def test_canonical_extractor_is_relabeling_invariant(self):
        a, b = self._world_pair()

        def extractor(canonical):
            # The canonical tuple is the sole input; no world labels are used.
            return [float(len(canonical[0])), float(len(canonical[1]))] + [0.0] * 21

        self.assertEqual(represent_canonical(a, extractor), represent_canonical(b, extractor))


if __name__ == "__main__":
    unittest.main()
