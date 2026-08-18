import unittest

from structure.theory_core import TheoryUnit
from structure.theory_graph import StructuralGraph
from structure.theory_relation import StructuralRelation
from structure.theory_representation_schema import (
    REPRESENTATION_DIM,
    REPRESENTATION_GROUPS,
    group_slices,
)


class TestTheoryMathMapping(unittest.TestCase):
    def make_units(self):
        return (
            TheoryUnit((0,), attributes={"role": "a"}),
            TheoryUnit((1,), attributes={"role": "b"}),
        )

    def test_structural_graph_is_explicit_g_equals_v_e(self):
        units = self.make_units()
        edge = StructuralRelation(0, 1, "adjacent", evidence={"source": "explicit"})
        graph = StructuralGraph(units, (edge,))
        self.assertEqual(graph.vertex_count, 2)
        self.assertEqual(graph.edge_count, 1)
        self.assertEqual(graph.as_world_components(), (units, (edge,)))

    def test_graph_rejects_edge_outside_vertex_domain(self):
        units = self.make_units()
        edge = StructuralRelation(0, 2, "adjacent")
        with self.assertRaises(ValueError):
            StructuralGraph(units, (edge,))

    def test_v4_schema_has_exactly_23_coordinates(self):
        self.assertEqual(REPRESENTATION_DIM, 23)
        self.assertEqual([size for _, size in REPRESENTATION_GROUPS], [3, 3, 3, 3, 3, 3, 5])
        slices = group_slices()
        self.assertEqual(slices["primitive_histogram"], slice(0, 3))
        self.assertEqual(slices["global_structural_counts"], slice(18, 23))


if __name__ == "__main__":
    unittest.main()
