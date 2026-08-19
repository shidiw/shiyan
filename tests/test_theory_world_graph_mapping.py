import unittest

from structure.theory_relation import StructuralRelation, relation_from_units
from structure.theory_world import StructuralWorld
from structure.theory_core import TheoryUnit


class TestTheoryWorldGraphMapping(unittest.TestCase):
    def test_graph_vertices_are_world_units_and_edges_are_exact_relations(self):
        units = (
            TheoryUnit((0,), {"label": "a"}),
            TheoryUnit((1,), {"label": "b"}),
        )
        relation = StructuralRelation(0, 1, "assembly", {"source": "explicit"})
        world = StructuralWorld(units, (relation,), {})

        self.assertEqual(world.graph.vertices, (0, 1))
        self.assertEqual(world.graph.edges, (relation,))

    def test_graph_does_not_infer_edges(self):
        units = (
            TheoryUnit((0,), {"primitive": "plane"}),
            TheoryUnit((1,), {"primitive": "plane"}),
        )
        world = StructuralWorld(units, (), {})
        self.assertEqual(world.graph.edges, ())

    def test_relation_endpoint_ids_must_be_distinct_and_nonnegative(self):
        with self.assertRaises(ValueError):
            StructuralRelation(-1, 1, "adjacent")
        with self.assertRaises(ValueError):
            StructuralRelation(0, 0, "adjacent")

    def test_relation_construction_is_explicit_not_unit_metadata_inference(self):
        source = TheoryUnit((0,), {"primitive": "plane"})
        target = TheoryUnit((1,), {"primitive": "plane"})
        relation = relation_from_units(
            source,
            target,
            source_id=0,
            target_id=1,
            relation_type="explicit",
            evidence={"rule": "supplied"},
        )
        self.assertEqual(relation.units, (0, 1))
        self.assertEqual(relation.relation_type, "explicit")
        self.assertEqual(dict(relation.evidence), {"rule": "supplied"})


if __name__ == "__main__":
    unittest.main()
