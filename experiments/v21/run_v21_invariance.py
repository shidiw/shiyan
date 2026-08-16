import os
import sys
import copy
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


# ============================================================
# Import v2.0 pipeline
# ============================================================

from experiments.v20.run_v20_end_to_end import run_pipeline


# ============================================================
# Deterministic rotation
# ============================================================

def rotation_matrix_x(theta):
    c = np.cos(theta)
    s = np.sin(theta)

    return np.array([
        [1, 0, 0],
        [0, c, -s],
        [0, s,  c]
    ], dtype=float)


def rotation_matrix_y(theta):
    c = np.cos(theta)
    s = np.sin(theta)

    return np.array([
        [ c, 0, s],
        [ 0, 1, 0],
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
    center = np.mean(points, axis=0)

    X = points - center

    return X @ R.T + center


def translate(points, t):
    return points + np.asarray(t, dtype=float)


# ============================================================
# Canonical structural signature
# ============================================================

def canonical_signature(world):

    objects = []

    for object_id, obj in world.objects.items():

        primitive = obj.get(
            "primitive",
            []
        )

        if isinstance(
            primitive,
            list
        ):

            primitive = tuple(
                sorted(
                    str(x)
                    for x in primitive
                )
            )

        else:

            primitive = (
                str(primitive),
            )

        # ------------------------------------------------
        # Structural parameters
        #
        # Remove coordinate-frame dependent quantities.
        # ------------------------------------------------

        parameters = obj.get(
            "parameters",
            []
        )

        if isinstance(
            parameters,
            dict
        ):

            parameters = [
                parameters
            ]

        intrinsic = []

        if isinstance(
            parameters,
            (list, tuple)
        ):

            for p in parameters:

                if not isinstance(
                    p,
                    dict
                ):
                    continue

                local = {}

                for key, value in sorted(
                    p.items(),
                    key=lambda x: str(x[0])
                ):

                    # ------------------------------------
                    # Coordinate-frame dependent
                    # ------------------------------------

                    if key in (
                        "center",
                        "origin",
                        "normal",
                        "axis",
                        "d",
                    ):
                        continue

                    arr = np.asarray(
                        value,
                        dtype=float
                    )

                    if arr.ndim == 0:

                        local[str(key)] = round(
                            float(arr),
                            8
                        )

                    else:

                        # Keep intrinsic magnitudes,
                        # not coordinate orientation.
                        flat = arr.reshape(-1)

                        local[str(key)] = tuple(
                            round(
                                float(
                                    np.linalg.norm(flat)
                                ),
                                8
                            ),
                        )

                intrinsic.append(
                    tuple(
                        local.items()
                    )
                )

        intrinsic = tuple(
            sorted(
                intrinsic,
                key=str
            )
        )

        # ------------------------------------------------
        # Energy
        # ------------------------------------------------

        energy = obj.get(
            "energy",
            0.0
        )

        try:

            energy = round(
                float(energy),
                8
            )

        except Exception:

            energy = 0.0

        # ------------------------------------------------
        # Structural signature
        # ------------------------------------------------

        objects.append({

            "primitive":
                primitive,

            "parameters":
                intrinsic,

            "points":
                int(
                    obj.get(
                        "points",
                        0
                    )
                ),

            "energy":
                energy
        })

    # ----------------------------------------------------
    # Object ordering must not depend on IDs
    # ----------------------------------------------------

    objects = sorted(
        objects,
        key=lambda x: (
            x["primitive"],
            x["points"],
            x["parameters"],
            x["energy"]
        )
    )


    print("\n[DEBUG] Canonical Objects")

    for i, obj in enumerate(objects):

        print(
            "Object",
            i
        )

        print(
            "  primitive:",
            obj["primitive"]
        )

        print(
            "  parameters:",
            obj["parameters"]
        )

        print(
            "  points:",
            obj["points"]
        )

        print(
            "  energy:",
            obj["energy"]
        )
    return objects
# ============================================================
# Structural hash
# ============================================================

def structural_hash(world):

    signature = canonical_signature(
        world
    )

    payload = pickle.dumps(
        signature,
        protocol=4
    )

    return hashlib.sha256(
        payload
    ).hexdigest()


# ============================================================
# Similarity
# ============================================================

def structural_similarity(
    world_a,
    world_b
):

    sig_a = canonical_signature(
        world_a
    )

    sig_b = canonical_signature(
        world_b
    )

    if len(sig_a) != len(sig_b):
        return 0.0

    if len(sig_a) == 0:
        return 1.0

    matches = 0

    for a, b in zip(sig_a, sig_b):

        if a["primitive"] != b["primitive"]:
            continue

        if a["points"] != b["points"]:
            continue

        matches += 1

    return matches / len(sig_a)


# ============================================================
# Test case
# ============================================================

def extract_world(result):
    """
    Normalize the output of the v2.0 pipeline.

    v2.0 run_pipeline() returns a result dictionary,
    while the invariance validator operates on
    StructuralWorldState.
    """

    # Already a world state
    if hasattr(result, "objects"):
        return result

    # Standard v2.0 result dictionary
    if isinstance(result, dict):

        if "world" in result:
            world = result["world"]

            if hasattr(world, "objects"):
                return world

        if "world_state" in result:
            world = result["world_state"]

            if hasattr(world, "objects"):
                return world

    raise TypeError(
        "Cannot extract StructuralWorldState "
        "from pipeline result: {}".format(
            type(result)
        )
    )


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

    world_a = extract_world(
        result_a
    )

    world_b = extract_world(
        result_b
    )

    hash_a = structural_hash(
        world_a
    )

    hash_b = structural_hash(
        world_b
    )

    similarity = structural_similarity(
        world_a,
        world_b
    )

    print(
        "Objects A:",
        len(world_a.objects)
    )

    print(
        "Objects B:",
        len(world_b.objects)
    )

    print(
        "Structural similarity:",
        similarity
    )

    print(
        "Hash A:",
        hash_a
    )

    print(
        "Hash B:",
        hash_b
    )

    return {
        "name":
            name,
     
        "similarity":
            similarity,

        "hash_equal":
            hash_a == hash_b,

        "objects_a":
            len(world_a.objects),

        "objects_b":
            len(world_b.objects)
    }


# ============================================================
# Main
# ============================================================

def main():

    print(
        "\n============================================================"
    )

    print(
        "Struct3D v2.1 Structural Invariance Validation"
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

    result_translation = run_case(
        "Translation Invariance",
        points,
        translated
    )

    if result_translation["similarity"] < 1.0:

        print(
            "\n[FAIL] Translation Invariance"
        )

        return 1

    print(
        "[PASS] Translation Invariance"
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

    result_rotation = run_case(
        "Rotation Invariance",
        points,
        rotated
    )

    if result_rotation["similarity"] < 1.0:

        print(
            "\n[FAIL] Rotation Invariance"
        )

        return 1

    print(
        "[PASS] Rotation Invariance"
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

    result_combined = run_case(
        "Rotation + Translation Invariance",
        points,
        transformed
    )

    if result_combined["similarity"] < 1.0:

        print(
            "\n[FAIL] Rotation + Translation Invariance"
        )

        return 1

    print(
        "[PASS] Rotation + Translation Invariance"
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print(
        "\n============================================================"
    )

    print(
        "Struct3D v2.1"
    )

    print(
        "INVARIANCE VALIDATION"
    )

    print(
        "============================================================"
    )

    print(
        "Translation:",
        result_translation["similarity"]
    )

    print(
        "Rotation:",
        result_rotation["similarity"]
    )

    print(
        "Rotation + Translation:",
        result_combined["similarity"]
    )

    print(
        "\nSTATUS: PASS"
    )

    return 0


if __name__ == "__main__":
    sys.exit(
        main()
    )
