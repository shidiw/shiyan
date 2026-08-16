import os
import sys
import numpy as np

ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../.."
    )
)

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from geometry.field import GeometryField
from graph.relation import StructuralGraph


def rotation_matrix():

    a = np.deg2rad(37.0)
    b = np.deg2rad(23.0)
    c = np.deg2rad(17.0)

    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(a), -np.sin(a)],
        [0, np.sin(a), np.cos(a)]
    ])

    Ry = np.array([
        [np.cos(b), 0, np.sin(b)],
        [0, 1, 0],
        [-np.sin(b), 0, np.cos(b)]
    ])

    Rz = np.array([
        [np.cos(c), -np.sin(c), 0],
        [np.sin(c), np.cos(c), 0],
        [0, 0, 1]
    ])

    return Rz @ Ry @ Rx


def rotate(points, R):

    center = np.mean(
        points,
        axis=0
    )

    return (
        (points - center)
        @ R.T
        +
        center
    )


def translate(points, t):

    return (
        points
        +
        np.asarray(
            t,
            dtype=float
        )
    )


def run_geometry(points):

    field = GeometryField(
        points,
        k=15
    ).compute()

    graph = StructuralGraph(
        k=30
    ).build(
        points,
        field["normals"],
        field["curvature"]
    )

    return field, graph


def main():

    print(
        "\n============================================================"
    )

    print(
        "Struct3D v2.2 Strict Graph Invariance"
    )

    print(
        "============================================================"
    )

    rng = np.random.default_rng(
        42
    )

    points = rng.normal(
        size=(3000, 3)
    )

    # ---------------------------------------------------------
    # Base
    # ---------------------------------------------------------

    field_a, graph_a = run_geometry(
        points
    )

    # ---------------------------------------------------------
    # Rotation
    # ---------------------------------------------------------

    R = rotation_matrix()

    rotated = rotate(
        points,
        R
    )

    field_b, graph_b = run_geometry(
        rotated
    )

    # ---------------------------------------------------------
    # Translation
    # ---------------------------------------------------------

    translated = translate(
        rotated,
        [10.0, -7.0, 4.0]
    )

    field_c, graph_c = run_geometry(
        translated
    )

    # =========================================================
    # Curvature
    # =========================================================

    curvature_ab = np.max(
        np.abs(
            field_a["curvature"]
            -
            field_b["curvature"]
        )
    )

    curvature_ac = np.max(
        np.abs(
            field_a["curvature"]
            -
            field_c["curvature"]
        )
    )

    print(
        "\nCurvature A/B max diff:",
        curvature_ab
    )

    print(
        "Curvature A/C max diff:",
        curvature_ac
    )

    # =========================================================
    # Graph weights
    # =========================================================

    weight_ab = np.max(
        np.abs(
            graph_a["weights"]
            -
            graph_b["weights"]
        )
    )

    weight_ac = np.max(
        np.abs(
            graph_a["weights"]
            -
            graph_c["weights"]
        )
    )

    print(
        "\nGraph weight A/B max diff:",
        weight_ab
    )

    print(
        "Graph weight A/C max diff:",
        weight_ac
    )

    # =========================================================
    # Graph size
    # =========================================================

    print(
        "\nEdges A:",
        len(graph_a["edges"])
    )

    print(
        "Edges B:",
        len(graph_b["edges"])
    )

    print(
        "Edges C:",
        len(graph_c["edges"])
    )

    # =========================================================
    # Statistics
    # =========================================================

    print(
        "\nWeight mean:"
    )

    print(
        "A:",
        np.mean(
            graph_a["weights"]
        )
    )

    print(
        "B:",
        np.mean(
            graph_b["weights"]
        )
    )

    print(
        "C:",
        np.mean(
            graph_c["weights"]
        )
    )

    # =========================================================
    # Assertions
    # =========================================================

    assert curvature_ab < 1e-10
    assert curvature_ac < 1e-10

    assert weight_ab < 1e-8
    assert weight_ac < 1e-8

    assert len(
        graph_a["edges"]
    ) == len(
        graph_b["edges"]
    )

    assert len(
        graph_a["edges"]
    ) == len(
        graph_c["edges"]
    )

    print(
        "\n[PASS] Strict Graph Invariance"
    )


if __name__ == "__main__":
    main()
