import unittest

from structure.theory_observation_pipeline import ObservationDerivedPipeline


class TestDebugObservationStage2E(unittest.TestCase):
    def test_dump_unit_formations(self):
        p = ObservationDerivedPipeline.from_points((
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
        ))
        for result in p.unit_formations:
            print("DEBUG", result.unit.indices, result.unit.attributes, result.stable, result.minimal_stable, result.margin_separated, result.materializable, p.energy.unit_energy(result.unit))
        print("DEBUG partitions", [(tuple(u.indices for u in q.units), float(p.energy(q))) for q in p.context.materialize_partitions()])
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
