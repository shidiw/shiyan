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


def rotation_matrix_z(theta):

    c = np.cos(theta)
    s = np.sin(theta)

    return np.array([
        [c, -s, 0.0],
        [s,  c, 0.0],
        [0.0, 0.0, 1.0]
    ])


def rotate(points, R):

    center = np.mean(
        points,
        axis=0
    )

    return (
        (points - center) @ R.T
        + center
    )


def main():

    points = np.load(
        "data/primitives.npy"
    )

    R = (
        rotation_matrix_z(
            np.deg2rad(37.0)
        )
    )

    rotated = rotate(
        points,
        R
    )

    # -----------------------------------------
    # Geometry
    # -----------------------------------------

    field_a = GeometryField(
        points,
        k=15
    ).compute()

    field_b = GeometryField(
        rotated,
        k=15
    ).compute()

    # -----------------------------------------
    # Curvature
    # -----------------------------------------

    curvature_diff = np.max(
        np.abs(
            field_a["curvature"]
            -
            field_b["curvature"]
        )
    )

    print(
        "Curvature max diff:",
        curvature_diff
    )

    # -----------------------------------------
    # Normal equivariance
    # -----------------------------------------

    normals_a = field_a["normals"]
    normals_b = field_b["normals"]

    rotated_normals_a = (
        normals_a @ R.T
    )

    direct_normal_error = np.mean(
        np.linalg.norm(
            rotated_normals_a
            -
            normals_b,
            axis=1
        )
    )

    sign_free_error = np.mean(
        np.minimum(
            np.linalg.norm(
                rotated_normals_a
                -
                normals_b,
                axis=1
            ),
            np.linalg.norm(
                rotated_normals_a
                +
                normals_b,
                axis=1
            )
        )
    )

    print(
        "Normal direct error:",
        direct_normal_error
    )

    print(
        "Normal sign-free error:",
        sign_free_error
    )

    # -----------------------------------------
    # Graph
    # -----------------------------------------

    graph_a = StructuralGraph(
        k=30
    ).build(
        points,
        field_a["normals"],
        field_a["curvature"]
    )

    graph_b = StructuralGraph(
        k=30
    ).build(
        rotated,
        field_b["normals"],
        field_b["curvature"]
    )

    weights_a = graph_a["weights"]
    weights_b = graph_b["weights"]

    print(
        "Graph edges A:",
        len(graph_a["edges"])
    )

    print(
        "Graph edges B:",
        len(graph_b["edges"])
    )

    print(
        "Weight mean A:",
        np.mean(weights_a)
    )

    print(
        "Weight mean B:",
        np.mean(weights_b)
    )

    print(
        "Weight max diff:",
        np.max(
            np.abs(
                weights_a
                -
                weights_b
            )
        )
    )


if __name__ == "__main__":
    main()