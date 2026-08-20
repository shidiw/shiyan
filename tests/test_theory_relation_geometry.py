import unittest

from structure.theory_core import TheoryUnit
from structure.theory_relation_formation import (
    GeometryRelationEvidence,
    form_geometry_relations,
    geometry_adjacency_q,
)


class TestStage3BGeometryRelation(unittest.TestCase):
    def setUp(self):
        self.units = (
            TheoryUnit((0, 1), {"geometry": "A"}),
            TheoryUnit((2, 3), {"geometry": "B"}),
            TheoryUnit((4, 5), {"geometry": "C"}),
        )

    def test_positive_boundary_measure_is_admissible(self):
        self.assertTrue(geometry_adjacency_q(GeometryRelationEvidence(2.5)))

    def test_zero_boundary_measure_is_not_admissible(self):
        self.assertFalse(geometry_adjacency_q(GeometryRelationEvidence(0.0)))

    def test_negative_or_nonfinite_measure_is_rejected(self):
        with self.assertRaises(ValueError):
            GeometryRelationEvidence(-1.0)
        with self.assertRaises(ValueError):
            GeometryRelationEvidence(float("nan"))
        with self.assertRaises(ValueError):
            GeometryRelationEvidence(float("inf"))

    def test_geometry_q_does_not_use_a_positive_threshold(self):
        self.assertTrue(geometry_adjacency_q(GeometryRelationEvidence(1e-15)))

    def test_only_admissible_candidate_pairs_are_materialized(self):
        result = form_geometry_relations(
            self.units,
            ((0, 1), (0, 2)),
            {
                (0, 1): GeometryRelationEvidence(1.0),
                (0, 2): GeometryRelationEvidence(0.0),
                (1, 2): GeometryRelationEvidence(3.0),
            },
        )
        self.assertEqual(len(result.relations), 1)
        self.assertEqual(result.relations[0].units, (0, 1))
        self.assertEqual(result.relations[0].relation_type, "adjacent")

    def test_missing_geometric_evidence_does_not_create_a_relation(self):
        result = form_geometry_relations(
            self.units,
            ((0, 1), (1, 2)),
            {(0, 1): GeometryRelationEvidence(1.0)},
        )
        self.assertEqual([r.units for r in result.relations], [(0, 1)])

    def test_relabeling_of_unit_ids_does_not_change_the_geometric_predicate(self):
        evidence = GeometryRelationEvidence(4.0)
        self.assertTrue(geometry_adjacency_q(evidence))


if __name__ == "__main__":
    unittest.main()
