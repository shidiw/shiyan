import os
import sys
import hashlib
import pickle
import numpy as np


# ============================================================
# Struct3D v2.3
# Structural Unit Invariance Validation
#
# Goal:
#
#   P
#   R(P)
#   R(P) + t
#
# must produce the same Structural Units.
#
# CPU only
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


# ============================================================
# Transformations
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

    center = np.mean(
        points,
        axis=0
    )

    X = points - center

    return (
        X @ R.T
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


# ============================================================
# Generic object getter
# ============================================================

def get_value(obj, key, default=None):

    if isinstance(obj, dict):

        return obj.get(
            key,
            default
        )

    return getattr(
        obj,
        key,
        default
    )


# ============================================================
# Extract units from pipeline result
# ============================================================

def extract_units(result):

    # --------------------------------------------------------
    # Direct list / tuple
    # --------------------------------------------------------

    if isinstance(result, (list, tuple)):

        if len(result) == 0:
            return []

        if all(
            hasattr(x, "points")
            or isinstance(x, dict)
            for x in result
        ):
            return list(result)


    # --------------------------------------------------------
    # Direct dictionary
    # --------------------------------------------------------

    if isinstance(result, dict):

        candidate_keys = [
            "units",
            "structural_units",
            "final_units"
        ]

        for key in candidate_keys:

            if key in result:

                units = result[key]

                if units is not None:
                    return list(units)


        # nested world
        for key in [
            "world",
            "world_state"
        ]:

            if key in result:

                world = result[key]

                units = get_value(
                    world,
                    "units",
                    None
                )

                if units is not None:

                    if isinstance(
                        units,
                        dict
                    ):
                        return list(
                            units.values()
                        )

                    return list(units)


    # --------------------------------------------------------
    # Object with units attribute
    # --------------------------------------------------------

    units = get_value(
        result,
        "units",
        None
    )

    if units is not None:

        if isinstance(
            units,
            dict
        ):
            return list(
                units.values()
            )

        return list(units)


    raise TypeError(
        "Cannot extract Structural Units "
        "from pipeline result: {}".format(
            type(result)
        )
    )


# ============================================================
# Convert indices to canonical tuple
# ============================================================

def unit_indices(unit):

    indices = get_value(
        unit,
        "indices",
        None
    )

    if indices is None:

        return None

    try:

        arr = np.asarray(
            indices
        ).reshape(-1)

        return tuple(
            sorted(
                int(x)
                for x in arr
            )
        )

    except Exception:

        return None


# ============================================================
# Primitive canonicalization
# ============================================================

def canonical_primitive(unit):

    primitive = get_value(
        unit,
        "primitive",
        "unknown"
    )

    if isinstance(
        primitive,
        (list, tuple, set)
    ):

        return tuple(
            sorted(
                str(x)
                for x in primitive
            )
        )

    return (
        str(primitive),
    )


# ============================================================
# Intrinsic parameter canonicalization
# ============================================================

def canonical_parameters(unit):

    parameters = get_value(
        unit,
        "parameters",
        {}
    )

    if parameters is None:
        return tuple()


    if isinstance(
        parameters,
        dict
    ):

        parameters = [
            parameters
        ]


    if not isinstance(
        parameters,
        (list, tuple)
    ):

        return (
            str(parameters),
        )


    result = []


    for p in parameters:

        if not isinstance(
            p,
            dict
        ):

            result.append(
                str(p)
            )

            continue


        local = {}


        for key, value in sorted(
            p.items(),
            key=lambda x: str(x[0])
        ):

            key = str(key)


            # ------------------------------------------------
            # Coordinate-frame dependent quantities
            #
            # These must NOT enter invariant signature.
            # ------------------------------------------------

            if key in (
                "center",
                "origin",
                "normal",
                "axis",
                "d"
            ):
                continue


            try:

                arr = np.asarray(
                    value,
                    dtype=float
                )

                if arr.ndim == 0:

                    local[key] = round(
                        float(arr),
                        8
                    )

                else:

                    flat = arr.reshape(-1)

                    # intrinsic magnitude
                    local[key] = round(
                        float(
                            np.linalg.norm(
                                flat
                            )
                        ),
                        8
                    )

            except Exception:

                local[key] = str(value)


        result.append(
            tuple(
                local.items()
            )
        )


    return tuple(
        sorted(
            result,
            key=str
        )
    )


# ============================================================
# Unit signature
# ============================================================

def unit_signature(unit):

    indices = unit_indices(
        unit
    )

    points = get_value(
        unit,
        "points",
        None
    )


    if points is not None:

        try:

            point_count = len(
                points
            )

        except Exception:

            point_count = 0

    elif indices is not None:

        point_count = len(
            indices
        )

    else:

        point_count = int(
            get_value(
                unit,
                "num_points",
                0
            )
        )


    energy = get_value(
        unit,
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


    return {

        "primitive":
            canonical_primitive(
                unit
            ),

        "parameters":
            canonical_parameters(
                unit
            ),

        "points":
            int(
                point_count
            ),

        "energy":
            energy,

        "indices":
            indices
    }


# ============================================================
# Structural Unit Canonical Signature
# ============================================================

def canonical_signature(units):

    signatures = []


    for unit in units:

        signatures.append(
            unit_signature(
                unit
            )
        )


    # --------------------------------------------------------
    # IDs/order must not affect result
    # --------------------------------------------------------

    signatures = sorted(
        signatures,
        key=lambda x: (
            x["indices"]
            if x["indices"] is not None
            else tuple(),

            x["primitive"],

            x["points"],

            x["parameters"],

            x["energy"]
        )
    )


    return signatures


# ============================================================
# Structural Unit Hash
# ============================================================

def structural_unit_hash(units):

    signature = canonical_signature(
        units
    )

    payload = pickle.dumps(
        signature,
        protocol=4
    )

    return hashlib.sha256(
        payload
    ).hexdigest()


# ============================================================
# Unit comparison
# ============================================================

def compare_units(
    units_a,
    units_b
):

    sig_a = canonical_signature(
        units_a
    )

    sig_b = canonical_signature(
        units_b
    )


    if len(sig_a) != len(sig_b):

        return {
            "similarity": 0.0,
            "count_equal": False,
            "membership_equal": False,
            "primitive_equal": False,
            "parameter_equal": False,
            "energy_equal": False
        }


    if len(sig_a) == 0:

        return {
            "similarity": 1.0,
            "count_equal": True,
            "membership_equal": True,
            "primitive_equal": True,
            "parameter_equal": True,
            "energy_equal": True
        }


    membership_equal = True
    primitive_equal = True
    parameter_equal = True
    energy_equal = True


    matches = 0


    for a, b in zip(
        sig_a,
        sig_b
    ):

        if a["indices"] != b["indices"]:

            membership_equal = False

        if a["primitive"] != b["primitive"]:

            primitive_equal = False

        if a["parameters"] != b["parameters"]:

            parameter_equal = False

        if abs(
            a["energy"]
            -
            b["energy"]
        ) > 1e-6:

            energy_equal = False


        if (
            a["indices"] == b["indices"]
            and
            a["primitive"] == b["primitive"]
            and
            a["points"] == b["points"]
        ):

            matches += 1


    similarity = (
        matches
        /
        len(sig_a)
    )


    return {

        "similarity":
            similarity,

        "count_equal":
            True,

        "membership_equal":
            membership_equal,

        "primitive_equal":
            primitive_equal,

        "parameter_equal":
            parameter_equal,

        "energy_equal":
            energy_equal
    }


# ============================================================
# Debug
# ============================================================

def print_units(
    name,
    units
):

    print(
        "\n[{}] Structural Units".format(
            name
        )
    )


    print(
        "Count:",
        len(units)
    )


    signatures = canonical_signature(
        units
    )


    for i, sig in enumerate(
        signatures
    ):

        print(
            "\nUnit",
            i
        )

        print(
            "  primitive:",
            sig["primitive"]
        )

        print(
            "  points:",
            sig["points"]
        )

        print(
            "  energy:",
            sig["energy"]
        )

        print(
            "  parameters:",
            sig["parameters"]
        )

        if sig["indices"] is not None:

            print(
                "  index count:",
                len(
                    sig["indices"]
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


    print_units(
        "A",
        units_a
    )

    print_units(
        "B",
        units_b
    )


    comparison = compare_units(
        units_a,
        units_b
    )


    hash_a = structural_unit_hash(
        units_a
    )

    hash_b = structural_unit_hash(
        units_b
    )


    print(
        "\nUnit count A:",
        len(units_a)
    )

    print(
        "Unit count B:",
        len(units_b)
    )

    print(
        "Similarity:",
        comparison["similarity"]
    )

    print(
        "Membership equal:",
        comparison["membership_equal"]
    )

    print(
        "Primitive equal:",
        comparison["primitive_equal"]
    )

    print(
        "Parameter equal:",
        comparison["parameter_equal"]
    )

    print(
        "Energy equal:",
        comparison["energy_equal"]
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
            comparison["similarity"],

        "count_equal":
            comparison["count_equal"],

        "membership_equal":
            comparison["membership_equal"],

        "primitive_equal":
            comparison["primitive_equal"],

        "parameter_equal":
            comparison["parameter_equal"],

        "energy_equal":
            comparison["energy_equal"],

        "hash_equal":
            hash_a == hash_b
    }


# ============================================================
# Main
# ============================================================

def main():

    print(
        "\n============================================================"
    )

    print(
        "Struct3D v2.3 Structural Unit Invariance"
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


    # ========================================================
    # Test 1
    # ========================================================

    result_translation = run_case(
        "Translation Invariance",
        points,
        translated
    )


    if (
        result_translation["similarity"] < 1.0
        or
        not result_translation["membership_equal"]
    ):

        print(
            "\n[FAIL] Translation Invariance"
        )

        return 1


    print(
        "[PASS] Translation Invariance"
    )


    # ========================================================
    # Test 2
    # ========================================================

    result_rotation = run_case(
        "Rotation Invariance",
        points,
        rotated
    )


    if (
        result_rotation["similarity"] < 1.0
        or
        not result_rotation["membership_equal"]
    ):

        print(
            "\n[FAIL] Rotation Invariance"
        )

        return 1


    print(
        "[PASS] Rotation Invariance"
    )


    # ========================================================
    # Test 3
    # ========================================================

    result_combined = run_case(
        "Rotation + Translation Invariance",
        points,
        transformed
    )


    if (
        result_combined["similarity"] < 1.0
        or
        not result_combined["membership_equal"]
    ):

        print(
            "\n[FAIL] Rotation + Translation Invariance"
        )

        return 1


    print(
        "[PASS] Rotation + Translation Invariance"
    )


    # ========================================================
    # Final
    # ========================================================

    print(
        "\n============================================================"
    )

    print(
        "Struct3D v2.3"
    )

    print(
        "STRUCTURAL UNIT INVARIANCE"
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


# ============================================================
# Entry
# ============================================================

if __name__ == "__main__":

    sys.exit(
        main()
    )
