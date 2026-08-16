import os
import sys
import hashlib
import pickle
import numpy as np

ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../.."
    )
)

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from structure.unit import StructuralUnit
from structure.hierarchy import StructuralHierarchy


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
        [s,  c, 0],
        [0,  0, 1]
    ], dtype=float)


def rotate(points, R):

    center = np.mean(
        points,
        axis=0
    )

    X = points - center

    return X @ R.T + center


def translate(points, t):

    return (
        points
        +
        np.asarray(
            t,
            dtype=float
        )
    )


# ============================================================
# Scene construction
# ============================================================

def make_sphere(
    center,
    radius,
    n,
    seed
):

    rng = np.random.default_rng(seed)

    dirs = rng.normal(
        size=(n, 3)
    )

    dirs /= (
        np.linalg.norm(
            dirs,
            axis=1,
            keepdims=True
        )
        +
        1e-12
    )

    return (
        np.asarray(center)
        +
        radius * dirs
    )


def make_cylinder(
    center,
    radius,
    height,
    n,
    seed
):

    rng = np.random.default_rng(seed)

    theta = rng.uniform(
        0,
        2 * np.pi,
        n
    )

    z = rng.uniform(
        -height / 2,
        height / 2,
        n
    )

    x = radius * np.cos(theta)
    y = radius * np.sin(theta)

    points = np.stack(
        [
            x,
            y,
            z
        ],
        axis=1
    )

    return (
        points
        +
        np.asarray(center)
    )


def build_units(points_list):

    units = []

    primitives = [
        "sphere",
        "sphere",
        "cylinder"
    ]

    for i, (points, primitive) in enumerate(
        zip(
            points_list,
            primitives
        )
    ):

        unit = StructuralUnit(
            points,
            primitive=primitive,
            indices=np.arange(
                len(points),
                dtype=np.int32
            )
        )

        unit.energy = {
            "value": 0.1 + 0.1 * i
        }

        units.append(unit)

    return units


# ============================================================
# Hierarchy construction
# ============================================================

def build_hierarchy(units):

    hierarchy = StructuralHierarchy()

    hierarchy.build(
        units
    )

    return hierarchy


# ============================================================
# Canonical hierarchy
# ============================================================

def canonical_hierarchy(
    hierarchy
):

    result = {
        "root_type":
            hierarchy.root.type,

        "children": []
    }

    for part in hierarchy.root.children:

        part_record = {
            "type":
                part.type,

            "children": []
        }

        for primitive in part.children:

            data = primitive.data

            energy = data.get(
                "energy"
            )

            if isinstance(
                energy,
                dict
            ):

                energy_value = energy.get(
                    "value",
                    0.0
                )

            else:

                try:
                    energy_value = float(
                        energy
                    )
                except Exception:
                    energy_value = 0.0

            primitive_record = {

                "type":
                    primitive.type,

                "primitive":
                    str(
                        data.get(
                            "primitive",
                            "unknown"
                        )
                    ),

                "points":
                    int(
                        data.get(
                            "points",
                            0
                        )
                    ),

                "energy":
                    round(
                        float(
                            energy_value
                        ),
                        8
                    )

                # IMPORTANT:
                #
                # center intentionally excluded.
                #
                # center is coordinate-frame dependent.
            }

            part_record[
                "children"
            ].append(
                primitive_record
            )

        result[
            "children"
        ].append(
            part_record
        )

    return result


# ============================================================
# Hash
# ============================================================

def hierarchy_hash(
    hierarchy
):

    signature = canonical_hierarchy(
        hierarchy
    )

    payload = pickle.dumps(
        signature,
        protocol=4
    )

    return hashlib.sha256(
        payload
    ).hexdigest()


# ============================================================
# Structural comparison
# ============================================================

def hierarchy_statistics(
    hierarchy
):

    parts = len(
        hierarchy.root.children
    )

    primitives = 0

    for part in hierarchy.root.children:

        primitives += len(
            part.children
        )

    return {
        "root":
            hierarchy.root.type,

        "parts":
            parts,

        "primitives":
            primitives
    }


def compare_hierarchy(
    name,
    hierarchy_a,
    hierarchy_b
):

    sig_a = canonical_hierarchy(
        hierarchy_a
    )

    sig_b = canonical_hierarchy(
        hierarchy_b
    )

    hash_a = hierarchy_hash(
        hierarchy_a
    )

    hash_b = hierarchy_hash(
        hierarchy_b
    )

    stats_a = hierarchy_statistics(
        hierarchy_a
    )

    stats_b = hierarchy_statistics(
        hierarchy_b
    )

    equal = (
        sig_a == sig_b
    )

    print()
    print("-" * 60)
    print(name)
    print("-" * 60)

    print(
        "Root A:",
        stats_a["root"]
    )

    print(
        "Root B:",
        stats_b["root"]
    )

    print(
        "Parts A:",
        stats_a["parts"]
    )

    print(
        "Parts B:",
        stats_b["parts"]
    )

    print(
        "Primitives A:",
        stats_a["primitives"]
    )

    print(
        "Primitives B:",
        stats_b["primitives"]
    )

    print(
        "Canonical equal:",
        equal
    )

    print(
        "Hash A:",
        hash_a
    )

    print(
        "Hash B:",
        hash_b
    )

    print(
        "Hash equal:",
        hash_a == hash_b
    )

    if equal and hash_a == hash_b:

        print(
            "[PASS]",
            name
        )

        return True

    print(
        "[FAIL]",
        name
    )

    return False


# ============================================================
# Main
# ============================================================

def main():

    print()
    print("=" * 60)
    print(
        "Struct3D v2.5 Non-Vacuous "
        "Hierarchy Invariance"
    )
    print("=" * 60)

    # --------------------------------------------------------
    # Explicit multi-unit scene
    # --------------------------------------------------------

    sphere_a = make_sphere(
        center=[0.0, 0.0, 0.0],
        radius=1.0,
        n=1000,
        seed=1
    )

    sphere_b = make_sphere(
        center=[2.5, 0.0, 0.0],
        radius=0.8,
        n=1000,
        seed=2
    )

    cylinder = make_cylinder(
        center=[5.0, 0.0, 0.0],
        radius=0.6,
        height=2.0,
        n=1000,
        seed=3
    )

    points_a = [
        sphere_a,
        sphere_b,
        cylinder
    ]

    units_a = build_units(
        points_a
    )

    hierarchy_a = build_hierarchy(
        units_a
    )

    print()
    print("[1] Base Hierarchy")

    stats = hierarchy_statistics(
        hierarchy_a
    )

    print(
        "Root:",
        stats["root"]
    )

    print(
        "Parts:",
        stats["parts"]
    )

    print(
        "Primitives:",
        stats["primitives"]
    )

    # --------------------------------------------------------
    # Structural non-vacuity
    # --------------------------------------------------------

    if stats["parts"] < 3:

        print(
            "[FAIL] Hierarchy is vacuous"
        )

        return 1

    if stats["primitives"] < 3:

        print(
            "[FAIL] Primitive hierarchy is vacuous"
        )

        return 1

    # --------------------------------------------------------
    # Rotation
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Translation
    # --------------------------------------------------------

    t = np.array([
        -13.0,
        5.0,
        8.0
    ])

    # --------------------------------------------------------
    # Translation
    # --------------------------------------------------------

    points_b = [
        translate(
            p,
            t
        )
        for p in points_a
    ]

    units_b = build_units(
        points_b
    )

    hierarchy_b = build_hierarchy(
        units_b
    )

    result_translation = compare_hierarchy(
        "Translation Invariance",
        hierarchy_a,
        hierarchy_b
    )

    # --------------------------------------------------------
    # Rotation
    # --------------------------------------------------------

    points_c = [
        rotate(
            p,
            R
        )
        for p in points_a
    ]

    units_c = build_units(
        points_c
    )

    hierarchy_c = build_hierarchy(
        units_c
    )

    result_rotation = compare_hierarchy(
        "Rotation Invariance",
        hierarchy_a,
        hierarchy_c
    )

    # --------------------------------------------------------
    # Rotation + Translation
    # --------------------------------------------------------

    points_d = [
        translate(
            rotate(
                p,
                R
            ),
            t
        )
        for p in points_a
    ]

    units_d = build_units(
        points_d
    )

    hierarchy_d = build_hierarchy(
        units_d
    )

    result_combined = compare_hierarchy(
        "Rotation + Translation Invariance",
        hierarchy_a,
        hierarchy_d
    )

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("Struct3D v2.5")
    print("HIERARCHY INVARIANCE")
    print("=" * 60)

    print(
        "Translation:",
        result_translation
    )

    print(
        "Rotation:",
        result_rotation
    )

    print(
        "Rotation + Translation:",
        result_combined
    )

    status = (
        result_translation
        and result_rotation
        and result_combined
    )

    if status:

        print()
        print(
            "STATUS: PASS"
        )

        return 0

    print()
    print(
        "STATUS: FAIL"
    )

    return 1


if __name__ == "__main__":

    sys.exit(
        main()
    )
