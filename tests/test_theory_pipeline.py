import unittest

from structure.theory_core import Partition, TheoryUnit
from structure.theory_pipeline import run_theory_pipeline


class TestTheoryPipeline(unittest.TestCase):
    def test_end_to_end_theory_composition(self):
        split = Partition(
            (TheoryUnit((0,), attributes={}), TheoryUnit((1,), attributes={})),
            (0, 1),
        )
        merged = Partition(
            (TheoryUnit((0, 1), attributes={}),),
            (0, 1),
        )
        # The energy selects the merged partition, so its world contains one
        # unit and cannot legally contain a relation (0, 1) between two units.
        result = run_theory_pipeline(
            (split, merged),
            lambda p: float(len(p.units)),
            (),
            lambda world: [float(world.unit_count)] * 23,
        )
        self.assertIs(result.partition_selection.partition, merged)
        self.assertEqual(result.world.unit_count, 1)
        self.assertEqual(len(result.representation.values), 23)
        self.assertIsNotNone(result.canonical)


if __name__ == "__main__":
    unittest.main()
