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
            unit = result.unit
            print("DEBUG UNIT", unit.indices, result.stable, result.minimal_stable, "E", p.energy.unit_energy(unit))
            for other in p.N_X(unit).alternatives:
                print("DEBUG NEIGHBOR", unit.indices, "vs", other.indices, "E", p.energy.unit_energy(other), "same", other == unit)
            print("DEBUG SUBS", unit.indices, [(sub.indices, p.energy.unit_energy(sub)) for sub in p.S_X(unit)])
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
