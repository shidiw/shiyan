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
from graph.relation import StructuralGraph
from structure.assembly import StructuralObjectAssembly


# ============================================================
# Rotation
# ============================================================

def rotation_matrix_z(theta):

    c = np.cos(theta)
    s = np.sin(theta)

    return np.array([
        [c, -s, 0],
        [s,  c, 0],
        [0,  0, 1]
    ], dtype=float)


def rotation_matrix_y(theta):

    c = np.cos(theta)
    s = np.sin(theta)

    return np.array([
        [ c, 0, s],
        [ 0, 1, 0],
        [-s, 0, c]
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
# Scene primitives
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

    dirs /= np.maximum(
        np.linalg.norm(
            dirs,
            axis=1,
            keepdims=True
        ),
        1e-12
    )

    return (
        np.asarray(center, dtype=float)
        +
        radius * dirs
    )


# ============================================================
# Scene
# ============================================================

def make_scene():

    centers = [
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [2.0, 0.0, 0.0],
        [3.0, 0.0, 0.0],
        [6.0, 0.0, 0.0],
    ]

    points_list = []

    for i, center in enumerate(centers):

        points_list.append(
            make_sphere(
                center=center,
                radius=0.35,
                n=300,
                seed=100 + i
            )
        )

    return points_list


# ============================================================
# Build units
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

        unit.energy = 0.1 + 0.01 * i

        units.append(unit)

    return units


# ============================================================
# Unit normals / curvature
#
# For this invariance experiment the geometric graph is
# constructed from rotation-invariant synthetic descriptors.
# ============================================================

def estimate_normals(points):

    center = np.mean(
        points,
        axis=0
    )

    normals = points - center

    norms = np.linalg.norm(
        normals,
        axis=1,
        keepdims=True
    )

    normals /= np.maximum(
        norms,
        1e-12
    )

    return normals


def estimate_curvature(points):

    center = np.mean(
        points,
        axis=0
    )

    radius = np.mean(
        np.linalg.norm(
            points - center,
            axis=1
        )
    )

    if radius < 1e-12:
        return np.zeros(
            len(points),
            dtype=float
        )

    return np.full(
        len(points),
        1.0 / radius,
        dtype=float
    )


# ============================================================
# Relation construction
# ============================================================

def build_relations(units):

    graph = StructuralGraph(
        k=15,
        sigma_n=0.5,
        sigma_k=0.05,
        alpha=1.0,
        beta=1.0
    )

    relations = []

    centers = []

    for unit in units:

        centers.append(
            unit.center()
        )

    centers = np.asarray(
        centers,
        dtype=float
    )

    # --------------------------------------------------------
    # Object-level relations
    #
    # We deliberately construct relations between structural
    # units using invariant center distances.
    # --------------------------------------------------------

    for i in range(len(units)):

        for j in range(i + 1, len(units)):

            distance = np.linalg.norm(
                centers[i] - centers[j]
            )

            if distance < 1.5:

                relation_type = "touching"

            elif distance < 4.0:

                relation_type = "near"

            else:

                relation_type = "separate"

            relations.append({

                "units": [
                    i,
                    j
                ],

                "type":
                    relation_type,

                "distance":
                    float(distance)
            })

    return relations


# ============================================================
# Assembly
# ============================================================

def build_assembly(units):

    relations = build_relations(
        units
    )

    assembler = StructuralObjectAssembly(
        threshold=0.6
    )

    objects = assembler.build(
        units,
        relations
    )

    return objects, relations


# ============================================================
# Canonical object signature
# ============================================================

def canonical_object(obj):

    primitives = []

    for part in obj.parts:

        primitive = getattr(
            part,
            "primitive",
            "unknown"
        )

        primitives.append(
            str(primitive)
        )

    primitives = sorted(
        primitives
    )

    return {

        "type":
            str(obj.type),

        "num_parts":
            int(len(obj.parts)),

        "primitives":
            primitives
    }


def canonical_assembly(objects):

    signatures = []

    for obj in objects:

        signatures.append(
            canonical_object(
                obj
            )
        )

    signatures.sort(
        key=lambda x: (
            x["type"],
            x["num_parts"],
            tuple(x["primitives"])
        )
    )

    return signatures


# ============================================================
# Hash
# ============================================================

def assembly_hash(objects):

    signature = canonical_assembly(
        objects
    )

    payload = pickle.dumps(
        signature,
        protocol=4
    )

    return hashlib.sha256(
        payload
    ).hexdigest()


# ============================================================
# Print
# ============================================================

def print_assembly(
    name,
    objects
):

    print()
    print(
        "[" + name + "] Objects"
    )

    print(
        "Count:",
        len(objects)
    )

    for i, obj in enumerate(objects):

        primitives = [
            getattr(
                p,
                "primitive",
                "unknown"
            )
            for p in obj.parts
        ]

        print(
            "Object",
            i,
            "type=",
            obj.type,
            "parts=",
            len(obj.parts),
            "primitives=",
            primitives
        )


# ============================================================
# Compare
# ============================================================

def compare_assembly(
    name,
    objects_a,
    objects_b
):

    sig_a = canonical_assembly(
        objects_a
    )

    sig_b = canonical_assembly(
        objects_b
    )

    hash_a = assembly_hash(
        objects_a
    )

    hash_b = assembly_hash(
        objects_b
    )

    equal = (
        sig_a == sig_b
    )

    print()
    print(
        "-" * 60
    )

    print(
        name
    )

    print(
        "-" * 60
    )

    print(
        "Objects A:",
        len(objects_a)
    )

    print(
        "Objects B:",
        len(objects_b)
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

    return (
        equal
        and
        hash_a == hash_b
    )


# ============================================================
# Main
# ============================================================

def main():

    print()
    print("=" * 60)
    print(
        "Struct3D v2.6.1 "
        "Assembly Invariance"
    )
    print("=" * 60)

    # --------------------------------------------------------
    # Base scene
    # --------------------------------------------------------

    base_points = make_scene()

    units_a = build_units(
        base_points
    )

    objects_a, relations_a = build_assembly(
        units_a
    )

    print()
    print(
        "[1] Base Assembly"
    )

    print(
        "Units:",
        len(units_a)
    )

    print(
        "Relations:",
        len(relations_a)
    )

    print_assembly(
        "A",
        objects_a
    )

    # --------------------------------------------------------
    # Translation
    # --------------------------------------------------------

    translated_points = [
        translate(
            p,
            [10.0, -5.0, 3.0]
        )
        for p in base_points
    ]

    units_b = build_units(
        translated_points
    )

    objects_b, relations_b = build_assembly(
        units_b
    )

    ok_translation = compare_assembly(
        "Translation Invariance",
        objects_a,
        objects_b
    )

    print(
        "[PASS]"
        if ok_translation
        else "[FAIL]",
        "Translation Invariance"
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
    )

    rotated_points = [
        rotate(
            p,
            R
        )
        for p in base_points
    ]

    units_c = build_units(
        rotated_points
    )

    objects_c, relations_c = build_assembly(
        units_c
    )

    ok_rotation = compare_assembly(
        "Rotation Invariance",
        objects_a,
        objects_c
    )

    print(
        "[PASS]"
        if ok_rotation
        else "[FAIL]",
        "Rotation Invariance"
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
            [-7.0, 4.0, 8.0]
        )
        for p in base_points
    ]

    units_d = build_units(
        transformed_points
    )

    objects_d, relations_d = build_assembly(
        units_d
    )

    ok_rt = compare_assembly(
        "Rotation + Translation Invariance",
        objects_a,
        objects_d
    )

    print(
        "[PASS]"
        if ok_rt
        else "[FAIL]",
        "Rotation + Translation Invariance"
    )

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print(
        "Struct3D v2.6.1"
    )
    print(
        "ASSEMBLY INVARIANCE"
    )
    print("=" * 60)

    print(
        "Translation:",
        ok_translation
    )

    print(
        "Rotation:",
        ok_rotation
    )

    print(
        "Rotation + Translation:",
        ok_rt
    )

    if (
        ok_translation
        and ok_rotation
        and ok_rt
    ):

        print()
        print(
            "STATUS: PASS"
        )

    else:

        print()
        print(
            "STATUS: FAIL"
        )


if __name__ == "__main__":

    main()
