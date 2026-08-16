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

from structure.primitive_selector import PrimitiveSelector
from structure.unit import StructuralUnit


# ============================================================
# Rotation
# ============================================================

def rotation_matrix_x(theta):

    c = np.cos(theta)
    s = np.sin(theta)

    return np.array([
        [1, 0, 0],
        [0, c, -s],
        [0, s, c]
    ], dtype=float)


def rotation_matrix_y(theta):

    c = np.cos(theta)
    s = np.sin(theta)

    return np.array([
        [c, 0, s],
        [0, 1, 0],
        [-s, 0, c]
    ], dtype=float)


def rotation_matrix_z(theta):

    c = np.cos(theta)
    s = np.sin(theta)

    return np.array([
        [c, -s, 0],
        [s, c, 0],
        [0, 0, 1]
    ], dtype=float)


def rotate(points, R):

    center = np.mean(
        points,
        axis=0
    )

    X = points - center

    return X @ R.T + center


# ============================================================
# Direct primitive test
# ============================================================

def test_selector(points_a, points_b):

    selector = PrimitiveSelector()

    print()
    print("=" * 60)
    print("PrimitiveSelector Rotation Invariance")
    print("=" * 60)

    print()
    print("[A] Original")

    result_a = selector.predict(
        StructuralUnit(
            points_a,
            primitive="unknown"
        )
    )

    print(
        "primitive:",
        result_a["primitive"]
    )

    print(
        "energy:",
        result_a["energy"]
    )

    print(
        "fit_energy:",
        result_a["fit_energy"]
    )

    print(
        "parameters:",
        result_a["parameters"]
    )

    print()
    print("[B] Rotated")

    result_b = selector.predict(
        StructuralUnit(
            points_b,
            primitive="unknown"
        )
    )

    print(
        "primitive:",
        result_b["primitive"]
    )

    print(
        "energy:",
        result_b["energy"]
    )

    print(
        "fit_energy:",
        result_b["fit_energy"]
    )

    print(
        "parameters:",
        result_b["parameters"]
    )

    print()
    print("=" * 60)
    print("Candidate Energy Comparison")
    print("=" * 60)

    for primitive in [
        "plane",
        "sphere",
        "cylinder"
    ]:

        ea = result_a["candidates"][
            primitive
        ]["energy"]

        eb = result_b["candidates"][
            primitive
        ]["energy"]

        print(
            primitive,
            "A =",
            ea,
            "B =",
            eb,
            "diff =",
            abs(ea - eb)
        )

    return result_a, result_b


# ============================================================
# Direct cylinder geometry test
# ============================================================

def test_cylinder_formula(points_a, points_b):

    print()
    print("=" * 60)
    print("Direct Cylinder Geometry Test")
    print("=" * 60)

    selector = PrimitiveSelector()

    a = selector.fit_cylinder(
        points_a
    )

    b = selector.fit_cylinder(
        points_b
    )

    print()
    print("Original radius:")
    print(a["parameters"]["radius"])

    print()
    print("Rotated radius:")
    print(b["parameters"]["radius"])

    print()
    print("Radius difference:")
    print(
        abs(
            a["parameters"]["radius"]
            -
            b["parameters"]["radius"]
        )
    )

    print()
    print("Original axis:")
    print(
        a["parameters"]["axis"]
    )

    print()
    print("Rotated axis:")
    print(
        b["parameters"]["axis"]
    )


# ============================================================
# Main
# ============================================================

def main():

    rng = np.random.default_rng(
        42
    )

    points = rng.normal(
        size=(3000, 3)
    )

    R = (
        rotation_matrix_z(
            np.deg2rad(37.0)
        )
        @
        rotation_matrix_y(
            np.deg2rad(23.0)
        )
        @
        rotation_matrix_x(
            np.deg2rad(17.0)
        )
    )

    rotated = rotate(
        points,
        R
    )

    print(
        "Input:",
        points.shape
    )

    test_cylinder_formula(
        points,
        rotated
    )

    test_selector(
        points,
        rotated
    )


if __name__ == "__main__":

    sys.exit(
        main()
    )