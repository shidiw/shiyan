import unittest

from structure.theory_core import TheoryUnit
from structure.theory_relation_formation import (
    RelationEvidence,
    form_relation,
    form_relations,
    relation_is_admissible,
)


class TestTheoryRelationFormation(unittest.TestCase):
    def setUp(self):
        self.units = (
            TheoryUnit(frozenset({0}), {}),
            TheoryUnit(frozenset({1}), {}),
            TheoryUnit(frozenset({2}), {}),
        )

    def test_relation_requires_explicit_predicate(self):
        with self.assertRaises(TypeError):
            relation_is_admissible(self.units[0], self.units[1], None)

    def test_rejected_pair_is_not_materialized(self):
        with self.assertRaises(ValueError):
            form_relation(
                self.units[0], self.units[1], 0, 1,
                RelationEvidence("assembly", {"source": "test"}),
                lambda _a, _b: False,
            )

    def test_accepted_pair_is_materialized_with_evidence(self):
        relation = form_relation(
            self.units[0], self.units[1], 0, 1,
            RelationEvidence("assembly", {"reason": "explicit"}),
            lambda _a, _b: True,
        )
        self.assertEqual((relation.source, relation.target), (0, 1))
        self.assertEqual(relation.relation_type, "assembly")
        self.assertEqual(relation.evidence["reason"], "explicit")

    def test_only_candidate_pairs_are_considered(self):
        relations = form_relations(
            self.units,
            ((0, 1), (1, 2)),
            lambda a, b: RelationEvidence("assembly", {"pair": (a, b)}),
            lambda a, b: a == 0 and b == 1,
        )
        self.assertEqual(len(relations.relations), 1)
        self.assertEqual(relations.relations[0].units, (0, 1))

    def test_no_relation_is_inferred_from_primitive_or_attribute_equality(self):
        relations = form_relations(
            self.units,
            ((0, 1), (1, 2)),
            lambda a, b: RelationEvidence("explicit", {}),
            lambda _a, _b: False,
        )
        self.assertEqual(relations.relations, ())

    def test_endpoint_domain_is_validated(self):
        with self.assertRaises(ValueError):
            form_relations(
                self.units, ((0, 3),), lambda a, b: RelationEvidence("x", {}), lambda a, b: True
            )

    def test_self_relation_is_rejected(self):
        with self.assertRaises(ValueError):
            form_relations(
                self.units, ((1, 1),), lambda a, b: RelationEvidence("x", {}), lambda a, b: True
            )

    def test_duplicate_candidate_pair_is_rejected(self):
        with self.assertRaises(ValueError):
            form_relations(
                self.units,
                ((0, 1), (0, 1)),
                lambda a, b: RelationEvidence("x", {}),
                lambda a, b: True,
            )


if __name__ == "__main__":
    unittest.main()
