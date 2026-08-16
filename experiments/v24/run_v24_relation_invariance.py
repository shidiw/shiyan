import os
import sys
import hashlib
import pickle
import numpy as np


# ============================================================
# ROOT
# ============================================================

ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../.."
    )
)

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


# ============================================================
# v2.0 pipeline
# ============================================================

from experiments.v20.run_v20_end_to_end import run_pipeline

from structure.relation import StructuralRelationGraph


# ============================================================
# Deterministic transformations
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
# World extraction
# ============================================================

def extract_world(result):

    if hasattr(
        result,
        "objects"
    ):
        return result

    if isinstance(
        result,
        dict
    ):

        if "world" in result:

            world = result["world"]

            if hasattr(
                world,
                "objects"
            ):
                return world

        if "world_state" in result:

            world = result["world_state"]

            if hasattr(
                world,
                "objects"
            ):
                return world

    raise TypeError(
        "Cannot extract StructuralWorldState "
        "from {}".format(
            type(result)
        )
    )


# ============================================================
# Unit extraction
# ============================================================

def extract_units(result):

    if isinstance(
        result,
        dict
    ):

        units = result.get(
            "units"
        )

        if units is not None:
            return units

    world = extract_world(
        result
    )

    if hasattr(
        world,
        "units"
    ):
        return world.units

    raise TypeError(
        "Cannot extract structural units"
    )


# ============================================================
# Relation builder
# ============================================================

def build_relations(units):

    relation_graph = StructuralRelationGraph()

    relations = relation_graph.build(
        units
    )

    return relations


# ============================================================
# Canonical relation signature
# ============================================================

def canonical_relation_signature(
    relations
):

    signature = []

    for r in relations:

        source = int(
            r["source"]
        )

        target = int(
            r["target"]
        )

        relation_type = str(
            r["type"]
        )

        distance = round(
            float(
                r["distance"]
            ),
            8
        )

        # ----------------------------------------------------
        # Relation is undirected.
        #
        # Canonicalize endpoint ordering.
        # ----------------------------------------------------

        if source > target:

            source, target = (
                target,
                source
            )

        signature.append(
            (
                source,
                target,
                relation_type,
                distance
            )
        )

    signature = sorted(
        signature
    )

    return tuple(
        signature
    )


# ============================================================
# Structural relation hash
# ============================================================

def relation_hash(
    relations
):

    signature = canonical_relation_signature(
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
# Type-only signature
# ============================================================

def relation_type_signature(
    relations
):

    signature = []

    for r in relations:

        source = int(
            r["source"]
        )

        target = int(
            r["target"]
        )

        relation_type = str(
            r["type"]
        )

        if source > target:

            source, target = (
                target,
                source
            )

        signature.append(
            (
                source,
                target,
                relation_type
            )
        )

    return tuple(
        sorted(
            signature
        )
    )


# ============================================================
# Relation distance comparison
# ============================================================

def max_distance_difference(
    relations_a,
    relations_b
):

    if len(relations_a) != len(
        relations_b
    ):
        return float("inf")

    a = canonical_relation_signature(
        relations_a
    )

    b = canonical_relation_signature(
        relations_b
    )

    if len(a) != len(b):

        return float("inf")

    max_diff = 0.0

    for x, y in zip(a, b):

        if x[:3] != y[:3]:

            return float("inf")

        diff = abs(
            x[3] - y[3]
        )

        max_diff = max(
            max_diff,
            diff
        )

    return max_diff


# ============================================================
# Debug printer
# ============================================================

def print_relations(
    name,
    relations
):

    print(
        "\n[{}] Relations".format(
            name
        )
    )

    print(
        "Count:",
        len(relations)
    )

    for r in relations:

        print(
            "  {} -- {} --> {}   distance={:.8f}".format(
                r["source"],
                r["type"],
                r["target"],
                r["distance"]
            )
        )


# ============================================================
# Run case
# ============================================================

def run_case(
    name,
    points_a,
    points_b
):

    print(
        "\n----------------------------------------"
    )

    print(
        name
    )

    print(
        "----------------------------------------"
    )

    result_a = run_pipeline(
        points_a
    )

    result_b = run_pipeline(
        points_b
    )

    units_a = extract_units(
        result_a
    )

    units_b = extract_units(
        result_b
    )

    print(
        "Units A:",
        len(units_a)
    )

    print(
        "Units B:",
        len(units_b)
    )

    if len(units_a) != len(units_b):

        print(
            "[FAIL] Unit count changed"
        )

        return {
            "name": name,
            "pass": False
        }

    relations_a = build_relations(
        units_a
    )

    relations_b = build_relations(
        units_b
    )

    print_relations(
        "A",
        relations_a
    )

    print_relations(
        "B",
        relations_b
    )

    signature_a = canonical_relation_signature(
        relations_a
    )

    signature_b = canonical_relation_signature(
        relations_b
    )

    type_signature_a = relation_type_signature(
        relations_a
    )

    type_signature_b = relation_type_signature(
        relations_b
    )

    hash_a = relation_hash(
        relations_a
    )

    hash_b = relation_hash(
        relations_b
    )

    distance_diff = max_distance_difference(
        relations_a,
        relations_b
    )

    type_equal = (
        type_signature_a
        ==
        type_signature_b
    )

    distance_equal = (
        distance_diff
        <
        1e-7
    )

    hash_equal = (
        hash_a
        ==
        hash_b
    )

    print(
        "\nRelation count A:",
        len(relations_a)
    )

    print(
        "Relation count B:",
        len(relations_b)
    )

    print(
        "Relation type equal:",
        type_equal
    )

    print(
        "Max distance difference:",
        distance_diff
    )

    print(
        "Distance equal:",
        distance_equal
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
        hash_equal
    )

    passed = (
        type_equal
        and distance_equal
    )

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

    return {
        "name": name,
        "pass": passed,
        "type_equal": type_equal,
        "distance_equal": distance_equal,
        "hash_equal": hash_equal,
        "relations_a": len(
            relations_a
        ),
        "relations_b": len(
            relations_b
        )
    }


# ============================================================
# Main
# ============================================================

def main():

    print(
        "\n============================================================"
    )

    print(
        "Struct3D v2.4 Structural Relation Invariance"
    )

    print(
        "============================================================"
    )

    # --------------------------------------------------------
    # Base scene
    # --------------------------------------------------------

    rng = np.random.default_rng(
        42
    )

    points = rng.normal(
        size=(3000, 3)
    )

    print(
        "\n[1] Base Scene"
    )

    print(
        "Input:",
        points.shape
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
            np.deg2rad(17.0)
        )
    )

    rotated = rotate(
        points,
        R
    )

    # --------------------------------------------------------
    # Translation
    # --------------------------------------------------------

    translation = np.array([
        10.0,
        -7.0,
        4.0
    ])

    translated = translate(
        points,
        translation
    )

    # --------------------------------------------------------
    # Rotation + Translation
    # --------------------------------------------------------

    transformed = translate(
        rotated,
        np.array([
            -13.0,
            5.0,
            8.0
        ])
    )

    # --------------------------------------------------------
    # Test 1
    # --------------------------------------------------------

    result_translation = run_case(
        "Translation Invariance",
        points,
        translated
    )

    if not result_translation["pass"]:

        return 1

    # --------------------------------------------------------
    # Test 2
    # --------------------------------------------------------

    result_rotation = run_case(
        "Rotation Invariance",
        points,
        rotated
    )

    if not result_rotation["pass"]:

        return 1

    # --------------------------------------------------------
    # Test 3
    # --------------------------------------------------------

    result_combined = run_case(
        "Rotation + Translation Invariance",
        points,
        transformed
    )

    if not result_combined["pass"]:

        return 1

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print(
        "\n============================================================"
    )

    print(
        "Struct3D v2.4"
    )

    print(
        "STRUCTURAL RELATION INVARIANCE"
    )

    print(
        "============================================================"
    )

    print(
        "Translation:",
        result_translation["pass"]
    )

    print(
        "Rotation:",
        result_rotation["pass"]
    )

    print(
        "Rotation + Translation:",
        result_combined["pass"]
    )

    print(
        "\nSTATUS: PASS"
    )

    return 0


if __name__ == "__main__":

    sys.exit(
        main()
    )

