import os
import sys
import json
import copy
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
from structure.optimize import StructuralOptimizer
from structure.primitive_selector import PrimitiveSelector


# ============================================================
# Struct3D v2.1
# Structural Emergence
#
# Experiment:
#
# coherent plane
#       ↓
# spatial fragmentation
#       ↓
# independent structural units
#       ↓
# variational optimization
#       ↓
# structural recovery
# ============================================================


def make_scene(
    seed=0,
    n_points=3000
):

    rng = np.random.default_rng(seed)

    x = rng.uniform(
        -3.0,
        3.0,
        n_points
    )

    y = rng.uniform(
        -3.0,
        3.0,
        n_points
    )

    z = rng.normal(
        0.0,
        0.01,
        n_points
    )

    points = np.column_stack([
        x,
        y,
        z
    ])

    return points


# ============================================================
# Fragmentation
# ============================================================

def make_fragmented_units(
    points
):

    x = points[:, 0]
    y = points[:, 1]

    masks = [

        (x < 0) & (y < 0),

        (x < 0) & (y >= 0),

        (x >= 0) & (y < 0),

        (x >= 0) & (y >= 0)

    ]

    units = []

    for mask in masks:

        pts = points[mask]

        if len(pts) == 0:
            continue

        units.append(
            StructuralUnit(
                pts,
                "unknown"
            )
        )

    return units


# ============================================================
# Primitive discovery
# ============================================================

def discover_primitives(
    units
):

    selector = PrimitiveSelector()

    for unit in units:

        result = selector.predict(
            unit
        )

        unit.primitive = (
            result["primitive"]
        )

        unit.parameters = (
            result["parameters"]
        )

        unit.energy = (
            result["energy"]
        )

    return units


# ============================================================
# Statistics
# ============================================================

def summarize(
    units
):

    return {

        "num_units":
            len(units),

        "primitives":
            [
                getattr(
                    u,
                    "primitive",
                    "unknown"
                )
                for u in units
            ],

        "energies":
            [
                float(
                    getattr(
                        u,
                        "energy",
                        0.0
                    )
                )
                for u in units
            ],

        "sizes":
            [
                len(
                    getattr(
                        u,
                        "points",
                        []
                    )
                )
                for u in units
            ]

    }


# ============================================================
# Single experiment
# ============================================================

def run_experiment(
    merge_threshold=-0.01,
    split_threshold=0.3,
    seed=0
):

    print(
        "\nExperiment"
    )

    print(
        {
            "merge_threshold":
                merge_threshold,

            "split_threshold":
                split_threshold
        }
    )

    points = make_scene(
        seed=seed
    )

    units = make_fragmented_units(
        points
    )

    units = discover_primitives(
        units
    )

    before = summarize(
        units
    )

    optimizer = StructuralOptimizer(
        merge_threshold=merge_threshold,
        split_threshold=split_threshold
    )

    optimized = optimizer.optimize(
        copy.deepcopy(units)
    )

    optimized = discover_primitives(
        optimized
    )

    after = summarize(
        optimized
    )

    print(
        "Before:",
        before
    )

    print(
        "After:",
        after
    )

    return {

        "merge_threshold":
            merge_threshold,

        "split_threshold":
            split_threshold,

        "before":
            before,

        "after":
            after

    }


# ============================================================
# Main
# ============================================================

def main():

    print(
        "\n========================================"
    )

    print(
        "Struct3D v2.1"
    )

    print(
        "Structural Emergence Validation"
    )

    print(
        "========================================"
    )

    # --------------------------------------------------------
    # Input
    # --------------------------------------------------------

    points = make_scene(
        seed=0
    )

    print(
        "\nInput:",
        points.shape
    )

    # --------------------------------------------------------
    # Experiments
    # --------------------------------------------------------

    experiments = [

        {
            "merge_threshold": -0.01,
            "split_threshold": 0.3
        },

        {
            "merge_threshold": -0.005,
            "split_threshold": 0.3
        },

        {
            "merge_threshold": -0.02,
            "split_threshold": 0.3
        },

        {
            "merge_threshold": -0.01,
            "split_threshold": 0.2
        },

        {
            "merge_threshold": -0.01,
            "split_threshold": 0.5
        }

    ]

    results = []

    for i, config in enumerate(
        experiments
    ):

        print(
            "\n----------------------------------------"
        )

        print(
            "Experiment",
            i
        )

        result = run_experiment(
            merge_threshold=
                config["merge_threshold"],

            split_threshold=
                config["split_threshold"],

            seed=0
        )

        results.append(
            result
        )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    output_dir = os.path.join(
        os.path.dirname(__file__),
        "results"
    )

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    output_path = os.path.join(
        output_dir,
        "structural_emergence_fragment_recovery.json"
    )

    with open(
        output_path,
        "w"
    ) as f:

        json.dump(
            results,
            f,
            indent=2
        )

    print(
        "\nSaved:",
        output_path
    )

    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    initial_units = results[0]["before"]["num_units"]

    final_units = [
        r["after"]["num_units"]
        for r in results
    ]

    print(
        "\nInitial units:",
        initial_units
    )

    print(
        "Final units:",
        final_units
    )

    if any(
        n < initial_units
        for n in final_units
    ):

        print(
            "\nStructural Emergence Experiment: PASS"
        )

    else:

        print(
            "\nStructural Emergence Experiment: "
            "NO MERGE OBSERVED"
        )

        print(
            "This is a valid scientific result:"
        )

        print(
            "current objective does not recover "
            "fragmented structure."
        )


if __name__ == "__main__":

    main()