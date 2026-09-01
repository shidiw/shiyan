import unittest
from structure.theory_observation_pipeline import ObservationDerivedPipeline

class TestDebugObservationPipeline(unittest.TestCase):
    def test_debug(self):
        points=((0.0,0.0,0.0),(1.0,0.0,0.0),(0.0,1.0,0.0),(0.0,0.0,1.0))
        p=ObservationDerivedPipeline.from_points(points)
        print('Amax',len(p.A_max),'Gamma',len(p.Gamma),'units',len(p.unit_family))
        for r in p.unit_formations:
            if len(r.unit.indices)==1:
                print('singleton',r.unit.indices,'stable',r.stable,'minimal',r.minimal_stable,'material',r.materializable,'E',p.energy.unit_energy(r.unit))
        print('materializable',len(p.materializable_units))
        print('partitions',len(p.partitions))

if __name__=='__main__': unittest.main()
