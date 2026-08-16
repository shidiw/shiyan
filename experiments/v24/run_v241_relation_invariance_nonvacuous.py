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
from structure.relation import StructuralRelationGraph


# ============================================================
# Transformations
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


def translate(points, t):

    return points + np.asarray(
        t,
        dtype=float
    )


# ============================================================
# Primitive generation
# ============================================================

def make_sphere(
    center,
    radius,
    n,
    seed
):

    rng = np.random.default_rng(seed)

    u = rng.uniform(
        -1.0,
        1.0,
        n
    )

    phi = rng.uniform(
        0.0,
        2.0 * np.pi,
        n
    )

    s = np.sqrt(
        1.0 - u * u
    )

    x = s * np.cos(phi)
    y = s * np.sin(phi)
    z = u

    points = np.column_stack([
        x,
        y,
        z
    ])

    return points * radius + np.asarray(
        center,
        dtype=float
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
        0.0,
        2.0 * np.pi,
        n
    )

    z = rng.uniform(
        -height / 2.0,
        height / 2.0,
        n
    )

    x = radius * np.cos(theta)
    y = radius * np.sin(theta)

    points = np.column_stack([
        x,
        y,
        z
    ])

    return points + np.asarray(
        center,
        dtype=float
    )


# ============================================================
# Build explicit multi-unit scene
# ============================================================

def build_scene():

    # Three spatially separated structural units.
    #
    # Distances between centers are intentionally chosen
    # so that the relation graph is non-empty.

    sphere_a = make_sphere(
        center=[0.0, 0.0, 0.0],
        radius=0.5,
        n=1000,
        seed=10
    )

    sphere_b = make_sphere(
        center=[1.0, 0.0, 0.0],
        radius=0.5,
        n=1000,
        seed=20
    )

    cylinder = make_cylinder(
        center=[3.0, 0.0, 0.0],
        radius=0.4,
        height=1.0,
        n=1000,
        seed=30
    )

    units = [

        StructuralUnit(
            sphere_a,
            primitive="sphere",
            indices=np.arange(0, 1000)
        ),

        StructuralUnit(
            sphere_b,
            primitive="sphere",
            indices=np.arange(1000, 2000)
        ),

        StructuralUnit(
            cylinder,
            primitive="cylinder",
            indices=np.arange(2000, 3000)
        )
    ]

    return units


# ============================================================
# Transform Units
# ============================================================

def transform_units(
    units,
    transform
):

    result = []

    for unit in units:

        points = transform(
            unit.points
        )

        result.append(
            StructuralUnit(
                points,
                primitive=unit.primitive,
                indices=None
            )
        )

    return result


# ============================================================
# Relation canonicalization
# ============================================================

def canonical_relations(
    relations
):

    canonical = []

    for r in relations:

        source = int(
            r["source"]
        )

        target = int(
            r["target"]
        )

        # Relation direction is irrelevant for
        # geometric invariance.

        if source > target:

            source, target = (
                target,
                source
            )

        canonical.append({

            "source":
                source,

            "target":
                target,

            "type":
                str(r["type"]),

            "distance":
                round(
                    float(r["distance"]),
                    8
                )
        })

    canonical.sort(
        key=lambda x: (
            x["source"],
            x["target"],
            x["type"],
            x["distance"]
        )
    )

    return canonical


# ============================================================
# Hash
# ============================================================

def relation_hash(
    relations
):

    signature = canonical_relations(
        relations
    )

    payload = pickle.dumps(
        signature,
        protocol=4
    )

    return hashlib.sha256(
        payload
    ).hexdigest()


# ============================================================
# Build relation graph
# ============================================================

def build_relations(
    units
):

    graph = StructuralRelationGraph(

        # Deliberately large enough to
        # create non-empty relations.

        near_threshold=1.5,

        touch_threshold=0.2
    )

    relations = graph.build(
        units
    )

    return relations


# ============================================================
# Compare
# ============================================================

def compare(
    name,
    units_a,
    units_b
):

    print()
    print("-" * 60)
    print(name)
    print("-" * 60)

    relations_a = build_relations(
        units_a
    )

    relations_b = build_relations(
        units_b
    )

    canonical_a = canonical_relations(
        relations_a
    )

    canonical_b = canonical_relations(
        relations_b
    )

    print()
    print("[A] Relations")

    for r in canonical_a:

        print(
            r
        )

    print()
    print("[B] Relations")

    for r in canonical_b:

        print(
            r
        )

    print()
    print(
        "Units A:",
        len(units_a)
    )

    print(
        "Units B:",
        len(units_b)
    )

    print(
        "Relations A:",
        len(canonical_a)
    )

    print(
        "Relations B:",
        len(canonical_b)
    )

    types_a = [
        r["type"]
        for r in canonical_a
    ]

    types_b = [
        r["type"]
        for r in canonical_b
    ]

    type_equal = (
        types_a == types_b
    )

    print(
        "Relation type equal:",
        type_equal
    )

    distances_equal = True

    max_diff = 0.0

    if len(canonical_a) != len(canonical_b):

        distances_equal = False

    else:

        for a, b in zip(
            canonical_a,
            canonical_b
        ):

            diff = abs(
                a["distance"]
                -
                b["distance"]
            )

            max_diff = max(
                max_diff,
                diff
            )

        distances_equal = (
            max_diff < 1e-7
        )

    print(
        "Max distance difference:",
        max_diff
    )

    print(
        "Distance equal:",
        distances_equal
    )

    hash_a = relation_hash(
        relations_a
    )

    hash_b = relation_hash(
        relations_b
    )

    print(
        "Hash A:",
        hash_a
    )

    print(
        "Hash B:",
        hash_b
    )

    hash_equal = (
        hash_a == hash_b
    )

    print(
        "Hash equal:",
        hash_equal
    )

    passed = (

        len(units_a) >= 2

        and

        len(units_b) >= 2

        and

        len(canonical_a) >= 1

        and

        len(canonical_b) >= 1

        and

        type_equal

        and

        distances_equal

        and

        hash_equal
    )

    print()

    if passed:

        print(
            "[PASS]",
            name
        )

    else:

        print(
            "[FAIL]",
            name
        )

    return passed


# ============================================================
# Main
# ============================================================

def main():

    print()
    print("=" * 60)
    print(
        "Struct3D v2.4.1 "
        "Non-Vacuous Relation Invariance"
    )
    print("=" * 60)

    units = build_scene()

    print()
    print("[1] Explicit Multi-Unit Scene")

    print(
        "Units:",
        len(units)
    )

    for i, unit in enumerate(units):

        print(
            "Unit",
            i,
            "primitive:",
            unit.primitive,
            "points:",
            unit.size(),
            "center:",
            unit.center()
        )

    # --------------------------------------------------------
    # Base relation graph
    # --------------------------------------------------------

    base_relations = build_relations(
        units
    )

    print()
    print(
        "Base relations:",
        len(base_relations)
    )

    if len(base_relations) == 0:

        print(
            "[FAIL] Base scene produced no relations"
        )

        return 1

    # --------------------------------------------------------
    # Translation
    # --------------------------------------------------------

    t = np.array([
        10.0,
        -7.0,
        4.0
    ])

    translated = transform_units(
        units,
        lambda p: translate(
            p,
            t
        )
    )

    result_translation = compare(
        "Translation Invariance",
        units,
        translated
    )

    if not result_translation:

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

    rotated = transform_units(
        units,
        lambda p: rotate(
            p,
            R
        )
    )

    result_rotation = compare(
        "Rotation Invariance",
        units,
        rotated
    )

    if not result_rotation:

        return 1

    # --------------------------------------------------------
    # Rotation + Translation
    # --------------------------------------------------------

    transformed = transform_units(
        units,
        lambda p: translate(
            rotate(
                p,
                R
            ),
            np.array([
                -13.0,
                5.0,
                8.0
            ])
        )
    )

    result_combined = compare(
        "Rotation + Translation Invariance",
        units,
        transformed
    )

    if not result_combined:

        return 1

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print(
        "Struct3D v2.4.1"
    )
    print(
        "NON-VACUOUS RELATION INVARIANCE"
    )
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

    print()
    print(
        "STATUS: PASS"
    )

    return 0


if __name__ == "__main__":

    sys.exit(
        main()
    )
