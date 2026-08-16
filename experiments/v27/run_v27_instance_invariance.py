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
from structure.assembly import StructuralObjectAssembly
from structure.instance import StructuralInstanceBuilder


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
# Primitive generation
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
        np.asarray(center, dtype=float)
        +
        radius * dirs
    )


# ============================================================
# Build Units
# ============================================================

def build_units(points_list):

    units = []

    for i, points in enumerate(points_list):

        unit = StructuralUnit(
            points,
            primitive="sphere",
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
# Build Assembly
# ============================================================

def build_assembly(units):

    relations = [
        {
            "source": 0,
            "target": 1,
            "type": "connected",
            "confidence": 1.0
        },
        {
            "source": 1,
            "target": 2,
            "type": "connected",
            "confidence": 1.0
        }
    ]

    assembler = StructuralObjectAssembly(
        threshold=0.6
    )

    objects = assembler.build(
        units,
        relations
    )

    return objects


# ============================================================
# Build Instances
# ============================================================

def build_instances(units):

    objects = build_assembly(
        units
    )

    builder = StructuralInstanceBuilder()

    instances = builder.build(
        units,
        objects
    )

    return instances


# ============================================================
# Canonical Instance Signature
# ============================================================

def instance_signature(instance):

    signature = {
        "canonical": instance.canonical_signature()
    }

    return signature


# ============================================================
# Hash
# ============================================================

def instance_hash(instance):

    signature = instance_signature(
        instance
    )

    payload = pickle.dumps(
        signature,
        protocol=4
    )

    return hashlib.sha256(
        payload
    ).hexdigest()


# ============================================================
# Statistics
# ============================================================

def statistics(instances):

    return {
        "instances": len(instances),
        "points": [
            len(inst.points)
            for inst in instances
        ],
        "primitives": [
            list(inst.primitives)
            for inst in instances
        ]
    }


# ============================================================
# Compare
# ============================================================

def compare(
    name,
    instances_a,
    instances_b
):

    print()
    print("-" * 60)
    print(name)
    print("-" * 60)

    print(
        "Instances A:",
        len(instances_a)
    )

    print(
        "Instances B:",
        len(instances_b)
    )

    hashes_a = [
        instance_hash(x)
        for x in instances_a
    ]

    hashes_b = [
        instance_hash(x)
        for x in instances_b
    ]

    signatures_a = [
        instance_signature(x)
        for x in instances_a
    ]

    signatures_b = [
        instance_signature(x)
        for x in instances_b
    ]

    equal = (
        signatures_a == signatures_b
    )

    hash_equal = (
        hashes_a == hashes_b
    )

    print(
        "Canonical equal:",
        equal
    )

    print(
        "Hash A:",
        hashes_a
    )

    print(
        "Hash B:",
        hashes_b
    )

    print(
        "Hash equal:",
        hash_equal
    )

    if not equal or not hash_equal:

        print(
            "[FAIL]",
            name
        )

        return False

    print(
        "[PASS]",
        name
    )

    return True


# ============================================================
# Main
# ============================================================

def main():

    print()
    print("=" * 60)
    print("Struct3D v2.7 Instance Identity Invariance")
    print("=" * 60)

    # --------------------------------------------------------
    # Base scene
    # --------------------------------------------------------

    points_a = make_sphere(
        center=[0.0, 0.0, 0.0],
        radius=1.0,
        n=300,
        seed=10
    )

    points_b = make_sphere(
        center=[2.5, 0.0, 0.0],
        radius=0.8,
        n=400,
        seed=20
    )

    points_c = make_sphere(
        center=[5.0, 0.5, 0.0],
        radius=0.6,
        n=500,
        seed=30
    )

    base_points = [
        points_a,
        points_b,
        points_c
    ]

    base_units = build_units(
        base_points
    )

    base_instances = build_instances(
        base_units
    )

    print()
    print("[1] Base Instances")

    base_stats = statistics(
        base_instances
    )

    print(
        "Instances:",
        base_stats["instances"]
    )

    print(
        "Points:",
        base_stats["points"]
    )

    print(
        "Primitives:",
        base_stats["primitives"]
    )

    # --------------------------------------------------------
    # Translation
    # --------------------------------------------------------

    translated_points = [
        translate(
            p,
            [10.0, -7.0, 4.0]
        )
        for p in base_points
    ]

    translated_units = build_units(
        translated_points
    )

    translated_instances = build_instances(
        translated_units
    )

    translation_ok = compare(
        "Translation Invariance",
        base_instances,
        translated_instances
    )

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
            np.deg2rad(19.0)
        )
    )

    rotated_points = [
        rotate(
            p,
            R
        )
        for p in base_points
    ]

    rotated_units = build_units(
        rotated_points
    )

    rotated_instances = build_instances(
        rotated_units
    )

    rotation_ok = compare(
        "Rotation Invariance",
        base_instances,
        rotated_instances
    )

    # --------------------------------------------------------
    # Rotation + Translation
    # --------------------------------------------------------

    transformed_points = [
        translate(
            rotate(
                p,
                R
            ),
            [11.0, -3.0, 6.0]
        )
        for p in base_points
    ]

    transformed_units = build_units(
        transformed_points
    )

    transformed_instances = build_instances(
        transformed_units
    )

    rigid_ok = compare(
        "Rotation + Translation Invariance",
        base_instances,
        transformed_instances
    )

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("Struct3D v2.7")
    print("INSTANCE IDENTITY INVARIANCE")
    print("=" * 60)

    print(
        "Translation:",
        translation_ok
    )

    print(
        "Rotation:",
        rotation_ok
    )

    print(
        "Rotation + Translation:",
        rigid_ok
    )

    if (
        translation_ok
        and rotation_ok
        and rigid_ok
    ):

        print()
        print("STATUS: PASS")

    else:

        print()
        print("STATUS: FAIL")

        raise RuntimeError(
            "Instance invariance validation failed."
        )


if __name__ == "__main__":

    main()
