import os
import sys
import json
import pickle
import hashlib
import numpy as np


ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../.."
    )
)

if ROOT not in sys.path:
    sys.path.insert(
        0,
        ROOT
    )


from structure.world_state import StructuralWorldState
from structure.world_validator import WorldStateValidator


# ==========================================================
# Hash
# ==========================================================

def canonicalize(value):
    """
    Convert world-state data into a deterministic
    JSON-compatible representation.
    """

    if isinstance(value, dict):

        items = []

        for key, val in value.items():

            items.append(
                (
                    str(key),
                    canonicalize(val)
                )
            )

        items.sort(
            key=lambda x: x[0]
        )

        return {
            key: val
            for key, val in items
        }

    if isinstance(value, (list, tuple)):

        return [
            canonicalize(v)
            for v in value
        ]

    if isinstance(value, np.ndarray):

        return canonicalize(
            value.tolist()
        )

    if isinstance(value, np.generic):

        return value.item()

    if isinstance(value, float):

        if np.isnan(value):
            return "NaN"

        if np.isinf(value):

            if value > 0:
                return "Infinity"

            return "-Infinity"

        return value

    if hasattr(value, "item"):

        try:
            return value.item()
        except Exception:
            pass

    return value


def state_hash(world):

    data = canonicalize(
        world.to_dict()
    )

    payload = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")

    return hashlib.sha256(
        payload
    ).hexdigest()


# ==========================================================
# Test basic world
# ==========================================================

def build_test_world():

    world = StructuralWorldState()

    world.add_object({
        "type": "single",
        "parts": [],
        "points": 1000,
        "center": [0.0, 0.0, 0.0],
        "primitive": ["plane"],
        "energy": 0.04
    })

    world.add_object({
        "type": "single",
        "parts": [],
        "points": 1000,
        "center": [-3.0, 0.0, 0.0],
        "primitive": ["sphere"],
        "energy": 0.05
    })

    world.add_object({
        "type": "single",
        "parts": [],
        "points": 1000,
        "center": [3.0, 0.0, 0.0],
        "primitive": ["sphere"],
        "energy": 0.04
    })

    world.add_instance({
        "object": 0,
        "points": 1000,
        "primitive": ["plane"],
        "center": [0.0, 0.0, 0.0]
    }, 0)

    world.add_instance({
        "object": 1,
        "points": 1000,
        "primitive": ["sphere"],
        "center": [-3.0, 0.0, 0.0]
    }, 1)

    world.add_instance({
        "object": 2,
        "points": 1000,
        "primitive": ["sphere"],
        "center": [3.0, 0.0, 0.0]
    }, 2)

    world.add_relation({
        "source": 0,
        "target": 1,
        "type": "separate",
        "distance": 3.0
    })

    world.add_relation({
        "source": 0,
        "target": 2,
        "type": "separate",
        "distance": 3.0
    })

    world.add_relation({
        "source": 1,
        "target": 2,
        "type": "separate",
        "distance": 6.0
    })

    world.add_reasoning({
        "type": "separate",
        "objects": [0, 1],
        "score": 1.0
    })

    world.add_reasoning({
        "type": "support",
        "objects": [0, 1],
        "score": 0.8
    })

    world.add_reasoning({
        "type": "support",
        "objects": [0, 2],
        "score": 0.8
    })

    world.add_prototype({
        "primitive": "plane",
        "count": 1,
        "confidence": 0.95
    }, 0)

    world.add_prototype({
        "primitive": "sphere",
        "count": 2,
        "confidence": 0.90
    }, 1)

    world.add_concept({
        "primitive": "plane",
        "instances": [0],
        "confidence": 0.75
    }, 0)

    world.add_concept({
        "primitive": "sphere",
        "instances": [1, 2],
        "confidence": 0.75
    }, 1)

    world.add_category({
        "name": "planar_surface",
        "concepts": [0],
        "instances": [0]
    }, 0)

    world.add_category({
        "name": "spherical_object",
        "concepts": [1],
        "instances": [1, 2]
    }, 1)

    return world


# ==========================================================
# Main
# ==========================================================

def main():

    print(
        "\n========================================"
    )

    print(
        "Struct3D v2.0 Validation"
    )

    print(
        "========================================"
    )

    # ------------------------------------------------------
    # 1
    # ------------------------------------------------------

    print(
        "\n[1] World State Construction"
    )

    world = build_test_world()

    print(
        "PASS"
    )

    # ------------------------------------------------------
    # 2
    # ------------------------------------------------------

    print(
        "\n[2] World Schema"
    )

    validator = WorldStateValidator()

    result = validator.validate(
        world
    )

    validator.show(
        result
    )

    if not result["valid"]:

        print(
            "\nFAILED: schema validation"
        )

        return 1

    # ------------------------------------------------------
    # 3
    # ------------------------------------------------------

    print(
        "\n[3] Statistics"
    )

    stats = world.statistics()

    for key, value in stats.items():

        print(
            "{}: {}".format(
                key,
                value
            )
        )

    # ------------------------------------------------------
    # 4
    # ------------------------------------------------------

    print(
        "\n[4] Persistence"
    )

    path = os.path.join(
        ROOT,
        "data",
        "world_state_v20.pkl"
    )

    world.save(
        path
    )

    if not os.path.exists(
        path
    ):

        print(
            "FAIL"
        )

        return 1

    loaded = StructuralWorldState.load(
        path
    )

    result_loaded = validator.validate(
        loaded
    )

    if not result_loaded["valid"]:

        print(
            "FAIL"
        )

        validator.show(
            result_loaded
        )

        return 1

    print(
        "PASS"
    )

    # ------------------------------------------------------
    # 5
    # ------------------------------------------------------

    print(
        "\n[5] Persistence Equality"
    )

    print(
        "\n[5b] Canonical State Equality"
    )

    state_a = canonicalize(
        world.to_dict()
    )

    state_b = canonicalize(
        loaded.to_dict()
    )

    if state_a != state_b:

        print("FAIL")

        print(
            "\nOriginal State:"
        )

        print(
            json.dumps(
                state_a,
                indent=2,
                sort_keys=True,
                ensure_ascii=False
            )
        )

        print(
            "\nLoaded State:"
        )

        print(
            json.dumps(
                state_b,
                indent=2,
                sort_keys=True,
                ensure_ascii=False
            )
        )

        return 1

    print("PASS")

    hash_a = state_hash(
        world
    )

    hash_b = state_hash(
        loaded
    )

    print(
        "Original:",
        hash_a
    )

    print(
        "Loaded:  ",
        hash_b
    )

    if hash_a != hash_b:

        print(
            "FAIL"
        )

        return 1

    print(
        "PASS"
    )

    # ------------------------------------------------------
    # 6
    # ------------------------------------------------------

    print(
        "\n[6] Deterministic Replay"
    )

    world_a = build_test_world()
    world_b = build_test_world()

    hash_a = state_hash(
        world_a
    )

    hash_b = state_hash(
        world_b
    )

    print(
        "Run A:",
        hash_a
    )

    print(
        "Run B:",
        hash_b
    )

    if hash_a != hash_b:

        print(
            "FAIL"
        )

        return 1

    print(
        "PASS"
    )

    # ------------------------------------------------------
    # 7
    # ------------------------------------------------------

    print(
        "\n[7] Final Consistency"
    )

    final = validator.validate(
        loaded
    )

    if final["valid"]:

        print(
            "PASS"
        )

    else:

        validator.show(
            final
        )

        return 1

    # ------------------------------------------------------
    # Final
    # ------------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "Struct3D v2.0"
    )

    print(
        "STATUS: FROZEN"
    )

    print(
        "========================================"
    )

    return 0


if __name__ == "__main__":

    sys.exit(
        main()
    )
