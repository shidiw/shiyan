import unittest

from structure.theory_observation_pipeline import ObservationDerivedPipeline


class TestHypothesisEliminationQuotientCommutation(unittest.TestCase):
    """The formerly external boundaries must commute with observation relabeling."""

    def setUp(self):
        self.points = (
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
        )
        # new observation order = old indices [2, 0, 3, 1]
        self.order = (2, 0, 3, 1)
        self.forward = {old: new for new, old in enumerate(self.order)}
        self.p = ObservationDerivedPipeline.from_points(self.points)
        self.q = ObservationDerivedPipeline.from_points(tuple(self.points[i] for i in self.order))

    def map_block(self, block):
        return tuple(sorted(self.forward[i] for i in block))

    def map_partition(self, blocks):
        return tuple(sorted((self.map_block(block) for block in blocks), key=lambda b: (b[0], len(b), b)))

    def test_A_and_Gamma_commute_exactly(self):
        p = {self.map_partition(x) for x in self.p.A_max}
        q = set(self.q.A_max)
        self.assertEqual(p, q)
        self.assertEqual({self.map_partition(x) for x in self.p.Gamma}, set(self.q.Gamma))

    def test_M_commutes_as_an_unordered_observation_derived_model_family(self):
        self.assertEqual(
            tuple((m.name, m.complexity) for m in self.p.M),
            tuple((m.name, m.complexity) for m in self.q.M),
        )

    def test_GB_commutes_under_vertex_relabeling(self):
        mapped = {
            (self.forward[s], self.forward[t], round(float(w), 12))
            for s, t, w in self.p.G_B.graph.edges
        }
        target = {(s, t, round(float(w), 12)) for s, t, w in self.q.G_B.graph.edges}
        self.assertEqual(mapped, target)

    def test_NX_and_SX_commute_under_support_relabeling(self):
        p_n = {
            self.map_block(key): {self.map_block(alt.indices) for alt in neighborhood.alternatives}
            for key, neighborhood in self.p.boundaries.N_X.neighborhoods
        }
        q_n = {
            key: {alt.indices for alt in neighborhood.alternatives}
            for key, neighborhood in self.q.boundaries.N_X.neighborhoods
        }
        self.assertEqual(p_n, q_n)

        p_s = {
            self.map_block(key): {self.map_block(u.indices) for u in values}
            for key, values in self.p.boundaries.S_X.subcandidates
        }
        q_s = {key: {u.indices for u in values} for key, values in self.q.boundaries.S_X.subcandidates}
        self.assertEqual(p_s, q_s)

    def test_CR_commutes_under_unit_and_pair_relabeling(self):
        old_units = self.p.C_R.units
        new_units = self.q.C_R.units
        old_to_new_unit = {tuple(u.indices): i for i, u in enumerate(old_units)}
        new_unit_by_support = {tuple(u.indices): i for i, u in enumerate(new_units)}
        mapped_pairs = {
            (new_unit_by_support[self.map_block(old_units[s].indices)],
             new_unit_by_support[self.map_block(old_units[t].indices)])
            for s, t in self.p.C_R.pairs
        }
        self.assertEqual(mapped_pairs, set(self.q.C_R.pairs))

    def test_Phi_X_is_quotient_invariant_on_the_world_path(self):
        self.assertEqual(self.p.representation().as_tuple(), self.q.representation().as_tuple())

    def test_pipeline_has_no_caller_supplied_boundary_path(self):
        audit = self.p.audit()
        self.assertTrue(audit["All_boundaries_observation_derived"])
        self.assertTrue(audit["All_boundaries_quotient_compatible"])
        self.assertIs(self.p.energy.observation_context, self.p.context)
        self.assertIs(self.p.Phi_X.context, self.p.context)


if __name__ == "__main__":
    unittest.main()
