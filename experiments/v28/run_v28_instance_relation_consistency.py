# ============================================================
# Struct3D v2.9
#
# Instance-Relation Consistency
#
# Test hierarchy:
#
#   Unit
#      |
#      | Assembly Relation
#      v
#   Object
#      |
#      | Structural Relation
#      v
#   Instance
#
# Required:
#
#   Objects = 3
#   Instances = 3
#   Object Relations = 1
#   Instance Relations = 1
#
# Invariance:
#
#   Translation
#   Rotation
#   Rotation + Translation
#
# CPU only
# ============================================================

import os
import sys
import hashlib
import pickle

import numpy as np


# ============================================================
# Root
# ============================================================

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


# ============================================================
# Imports
# ============================================================

from structure.unit import StructuralUnit

from structure.assembly import (
    StructuralObjectAssembly
)

from structure.instance import (
    StructuralInstanceBuilder
)


# ============================================================
# Rotation
# ============================================================

def rotation_matrix_x(
    theta
):

    c = np.cos(
        theta
    )

    s = np.sin(
        theta
    )

    return np.array(
        [
            [1, 0, 0],
            [0, c, -s],
            [0, s, c]
        ],
        dtype=float
    )


def rotation_matrix_y(
    theta
):

    c = np.cos(
        theta
    )

    s = np.sin(
        theta
    )

    return np.array(
        [
            [c, 0, s],
            [0, 1, 0],
            [-s, 0, c]
        ],
        dtype=float
    )


def rotation_matrix_z(
    theta
):

    c = np.cos(
        theta
    )

    s = np.sin(
        theta
    )

    return np.array(
        [
            [c, -s, 0],
            [s, c, 0],
            [0, 0, 1]
        ],
        dtype=float
    )


def rotate(
    points,
    R
):

    center = np.mean(
        points,
        axis=0
    )

    X = (
        points
        -
        center
    )

    return (
        X @ R.T
        +
        center
    )


def translate(
    points,
    t
):

    return (
        points
        +
        np.asarray(
            t,
            dtype=float
        )
    )


# ============================================================
# Primitive Generation
# ============================================================

def make_sphere(
    center,
    radius,
    n,
    seed
):

    rng = np.random.default_rng(
        seed
    )

    dirs = rng.normal(
        size=(
            n,
            3
        )
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
        np.asarray(
            center,
            dtype=float
        )
        +
        radius * dirs
    )


# ============================================================
# Scene
# ============================================================

def make_scene():

    points_list = [

        make_sphere(
            center=[
                0.0,
                0.0,
                0.0
            ],
            radius=1.0,
            n=150,
            seed=10
        ),

        make_sphere(
            center=[
                2.2,
                0.0,
                0.0
            ],
            radius=0.8,
            n=150,
            seed=20
        ),

        make_sphere(
            center=[
                4.4,
                0.0,
                0.0
            ],
            radius=0.7,
            n=150,
            seed=30
        ),

        make_sphere(
            center=[
                8.0,
                0.0,
                0.0
            ],
            radius=0.9,
            n=150,
            seed=40
        ),

        make_sphere(
            center=[
                10.3,
                0.0,
                0.0
            ],
            radius=0.8,
            n=150,
            seed=50
        )
    ]

    return points_list


# ============================================================
# Build Units
# ============================================================

def build_units(
    points_list
):

    units = []

    for i, points in enumerate(
        points_list
    ):

        unit = StructuralUnit(
            points,
            primitive="sphere",
            indices=np.arange(
                len(points),
                dtype=np.int32
            )
        )

        unit.energy = {
            "value":
                0.1
                +
                0.1 * i
        }

        units.append(
            unit
        )

    return units


# ============================================================
# Unit Relations
#
# Five Units:
#
#   0 --same_object-- 1
#
#   1 --connected---- 2
#
#   3 --same_object-- 4
#
#
# Therefore:
#
#   Object 0 = {0,1}
#   Object 1 = {2}
#   Object 2 = {3,4}
#
# Structural relation:
#
#   Object 0 --connected-- Object 1
#
# ============================================================

def build_unit_relations():

    relations = [

        # ----------------------------------------------------
        # Assembly relation
        # ----------------------------------------------------

        {
            "source": 0,
            "target": 1,
            "type": "same_object",
            "confidence": 1.0
        },

        # ----------------------------------------------------
        # Structural relation
        # ----------------------------------------------------

        {
            "source": 1,
            "target": 2,
            "type": "connected",
            "confidence": 1.0
        },

        # ----------------------------------------------------
        # Assembly relation
        # ----------------------------------------------------

        {
            "source": 3,
            "target": 4,
            "type": "same_object",
            "confidence": 1.0
        }
    ]

    return relations


# ============================================================
# Build Objects
# ============================================================

def build_objects(
    units,
    relations
):

    assembler = StructuralObjectAssembly(
        threshold=0.6
    )

    objects = assembler.build(
        units,
        relations
    )

    return (
        assembler,
        objects
    )


# ============================================================
# Object Relation Projection
# ============================================================

def project_object_relations(
    assembler,
    units,
    objects,
    relations
):

    return assembler.project_relations(
        units,
        objects,
        relations
    )


# ============================================================
# Build Instances
# ============================================================

def build_instances(
    units,
    objects
):

    builder = (
        StructuralInstanceBuilder()
    )

    instances = builder.build(
        units,
        objects
    )

    return instances


# ============================================================
# Object -> Instance Mapping
# ============================================================

def build_object_instance_map(
    objects,
    instances
):

    mapping = {}

    for instance_id, instance in enumerate(
        instances
    ):

        object_id = getattr(
            instance,
            "id",
            None
        )

        if object_id is None:

            object_id = instance_id

        try:

            object_id = int(
                object_id
            )

        except Exception:

            object_id = instance_id

        mapping[
            object_id
        ] = instance_id

    # --------------------------------------------------------
    # Safety fallback
    # --------------------------------------------------------

    if len(mapping) != len(
        objects
    ):

        mapping = {

            object_id:
                instance_id

            for instance_id, object_id
            in enumerate(
                range(
                    len(objects)
                )
            )
        }

    return mapping


# ============================================================
# Instance Relation Projection
# ============================================================

def project_instance_relations(
    object_relations,
    object_instance_map
):

    projected = []

    seen = set()

    for relation in object_relations:

        if not isinstance(
            relation,
            dict
        ):

            continue

        source = relation.get(
            "source"
        )

        target = relation.get(
            "target"
        )

        relation_type = relation.get(
            "type",
            relation.get(
                "relation",
                "unknown"
            )
        )

        try:

            source = int(
                source
            )

            target = int(
                target
            )

        except Exception:

            continue

        if (
            source not in
            object_instance_map
        ):

            continue

        if (
            target not in
            object_instance_map
        ):

            continue

        instance_source = (
            object_instance_map[
                source
            ]
        )

        instance_target = (
            object_instance_map[
                target
            ]
        )

        # ----------------------------------------------------
        # Internal relation
        # ----------------------------------------------------

        if (
            instance_source
            ==
            instance_target
        ):

            continue

        # ----------------------------------------------------
        # Canonical endpoint ordering
        # ----------------------------------------------------

        a = min(
            instance_source,
            instance_target
        )

        b = max(
            instance_source,
            instance_target
        )

        key = (
            a,
            b,
            str(
                relation_type
            )
        )

        if key in seen:

            continue

        seen.add(
            key
        )

        projected.append({

            "source":
                a,

            "target":
                b,

            "type":
                str(
                    relation_type
                )
        })

    projected.sort(
        key=lambda r: (
            r["source"],
            r["target"],
            r["type"]
        )
    )

    return projected


# ============================================================
# Canonical Relations
# ============================================================

def canonical_relations(
    relations
):

    canonical = []

    for relation in relations:

        if not isinstance(
            relation,
            dict
        ):

            continue

        try:

            source = int(
                relation[
                    "source"
                ]
            )

            target = int(
                relation[
                    "target"
                ]
            )

        except Exception:

            continue

        canonical.append({

            "source":
                source,

            "target":
                target,

            "type":
                str(
                    relation.get(
                        "type",
                        "unknown"
                    )
                )
        })

    canonical.sort(
        key=lambda r: (
            r["source"],
            r["target"],
            r["type"]
        )
    )

    return canonical


# ============================================================
# Relation Hash
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
# Object Statistics
# ============================================================

def object_statistics(
    objects
):

    return {

        "objects":
            len(objects),

        "parts":
            [
                obj.num_parts
                for obj in objects
            ],

        "points":
            [
                obj.num_points
                for obj in objects
            ]
    }


# ============================================================
# Instance Statistics
# ============================================================

def instance_statistics(
    instances
):

    return {

        "instances":
            len(instances),

        "points":
            [
                len(
                    inst.points
                )
                for inst in instances
            ],

        "primitives":
            [
                list(
                    inst.primitives
                )
                for inst in instances
            ]
    }


# ============================================================
# Complete Pipeline
# ============================================================

def build_pipeline(
    points_list
):

    # --------------------------------------------------------
    # Units
    # --------------------------------------------------------

    units = build_units(
        points_list
    )

    # --------------------------------------------------------
    # Unit relations
    # --------------------------------------------------------

    unit_relations = (
        build_unit_relations()
    )

    # --------------------------------------------------------
    # Objects
    # --------------------------------------------------------

    assembler, objects = (
        build_objects(
            units,
            unit_relations
        )
    )

    # --------------------------------------------------------
    # Object relations
    # --------------------------------------------------------

    object_relations = (
        project_object_relations(
            assembler,
            units,
            objects,
            unit_relations
        )
    )

    # --------------------------------------------------------
    # Instances
    # --------------------------------------------------------

    instances = build_instances(
        units,
        objects
    )

    # --------------------------------------------------------
    # Object -> Instance mapping
    # --------------------------------------------------------

    object_instance_map = (
        build_object_instance_map(
            objects,
            instances
        )
    )

    # --------------------------------------------------------
    # Instance relations
    # --------------------------------------------------------

    instance_relations = (
        project_instance_relations(
            object_relations,
            object_instance_map
        )
    )

    return {

        "units":
            units,

        "objects":
            objects,

        "instances":
            instances,

        "unit_relations":
            unit_relations,

        "object_relations":
            object_relations,

        "instance_relations":
            instance_relations,

        "assembler":
            assembler,

        "object_instance_map":
            object_instance_map
    }


# ============================================================
# Statistics
# ============================================================

def statistics(
    result
):

    return {

        "units":
            len(
                result[
                    "units"
                ]
            ),

        "objects":
            len(
                result[
                    "objects"
                ]
            ),

        "instances":
            len(
                result[
                    "instances"
                ]
            ),

        "unit_relations":
            len(
                result[
                    "unit_relations"
                ]
            ),

        "object_relations":
            len(
                result[
                    "object_relations"
                ]
            ),

        "instance_relations":
            len(
                result[
                    "instance_relations"
                ]
            )
    }


# ============================================================
# Canonical Object Signature
# ============================================================

def canonical_object_signature(
    objects
):

    signatures = []

    for obj in objects:

        part_sizes = sorted(
            [
                len(
                    getattr(
                        part,
                        "points",
                        []
                    )
                )
                for part in obj.parts
            ]
        )

        primitives = sorted(
            [
                str(
                    getattr(
                        part,
                        "primitive",
                        "unknown"
                    )
                )
                for part in obj.parts
            ]
        )

        signatures.append({

            "parts":
                len(
                    obj.parts
                ),

            "part_sizes":
                tuple(
                    part_sizes
                ),

            "primitives":
                tuple(
                    primitives
                ),

            "type":
                str(
                    obj.type
                )
        })

    signatures.sort(
        key=lambda x: (
            x["parts"],
            x["part_sizes"],
            x["primitives"],
            x["type"]
        )
    )

    return signatures


# ============================================================
# Canonical Instance Signature
# ============================================================

def canonical_instance_signature(
    instances
):

    signatures = []

    for instance in instances:

        canonical = (
            instance.canonical_signature()
        )

        signatures.append(
            canonical
        )

    signatures.sort(
        key=lambda x: repr(
            x
        )
    )

    return signatures


# ============================================================
# Scene Relation Signature
# ============================================================

def scene_relation_signature(
    result
):

    return {

        "object_relations":
            canonical_relations(
                result[
                    "object_relations"
                ]
            ),

        "instance_relations":
            canonical_relations(
                result[
                    "instance_relations"
                ]
            )
    }


# ============================================================
# Scene Relation Hash
# ============================================================

def scene_relation_hash(
    result
):

    signature = (
        scene_relation_signature(
            result
        )
    )

    payload = pickle.dumps(
        signature,
        protocol=4
    )

    return hashlib.sha256(
        payload
    ).hexdigest()


# ============================================================
# Compare
# ============================================================

def compare(
    name,
    result_a,
    result_b
):

    object_rel_a = (
        canonical_relations(
            result_a[
                "object_relations"
            ]
        )
    )

    object_rel_b = (
        canonical_relations(
            result_b[
                "object_relations"
            ]
        )
    )

    instance_rel_a = (
        canonical_relations(
            result_a[
                "instance_relations"
            ]
        )
    )

    instance_rel_b = (
        canonical_relations(
            result_b[
                "instance_relations"
            ]
        )
    )

    object_hash_a = (
        relation_hash(
            result_a[
                "object_relations"
            ]
        )
    )

    object_hash_b = (
        relation_hash(
            result_b[
                "object_relations"
            ]
        )
    )

    instance_hash_a = (
        relation_hash(
            result_a[
                "instance_relations"
            ]
        )
    )

    instance_hash_b = (
        relation_hash(
            result_b[
                "instance_relations"
            ]
        )
    )

    object_equal = (
        object_rel_a
        ==
        object_rel_b
    )

    instance_equal = (
        instance_rel_a
        ==
        instance_rel_b
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
        "Object Relations A:",
        object_rel_a
    )

    print(
        "Object Relations B:",
        object_rel_b
    )

    print(
        "Instance Relations A:",
        instance_rel_a
    )

    print(
        "Instance Relations B:",
        instance_rel_b
    )

    print(
        "Object Canonical equal:",
        object_equal
    )

    print(
        "Instance Canonical equal:",
        instance_equal
    )

    print(
        "Object Hash A:",
        object_hash_a
    )

    print(
        "Object Hash B:",
        object_hash_b
    )

    print(
        "Object Hash equal:",
        object_hash_a
        ==
        object_hash_b
    )

    print(
        "Instance Hash A:",
        instance_hash_a
    )

    print(
        "Instance Hash B:",
        instance_hash_b
    )

    print(
        "Instance Hash equal:",
        instance_hash_a
        ==
        instance_hash_b
    )

    passed = (

        object_equal

        and

        instance_equal

        and

        object_hash_a
        ==
        object_hash_b

        and

        instance_hash_a
        ==
        instance_hash_b
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

    return passed


# ============================================================
# Validate Base Scene
# ============================================================

def validate_base_scene(
    result
):

    objects = result[
        "objects"
    ]

    instances = result[
        "instances"
    ]

    unit_relations = result[
        "unit_relations"
    ]

    object_relations = result[
        "object_relations"
    ]

    instance_relations = result[
        "instance_relations"
    ]

    print()
    print(
        "[1] Base Scene"
    )

    print(
        "Units:",
        len(
            result[
                "units"
            ]
        )
    )

    print(
        "Objects:",
        len(
            objects
        )
    )

    print(
        "Instances:",
        len(
            instances
        )
    )

    print(
        "Unit Relations:",
        len(
            unit_relations
        )
    )

    print(
        "Object Relations:",
        len(
            object_relations
        )
    )

    print(
        "Instance Relations:",
        len(
            instance_relations
        )
    )

    print()

    print(
        "Object parts:",
        [
            obj.num_parts
            for obj in objects
        ]
    )

    print(
        "Instance points:",
        [
            len(
                inst.points
            )
            for inst in instances
        ]
    )

    print(
        "Object Relations:",
        canonical_relations(
            object_relations
        )
    )

    print(
        "Instance Relations:",
        canonical_relations(
            instance_relations
        )
    )

    # --------------------------------------------------------
    # Required structure
    # --------------------------------------------------------

    expected_object_parts = [
        2,
        1,
        2
    ]

    expected_instance_points = [
        300,
        150,
        300
    ]

    expected_object_relations = [
        {
            "source": 0,
            "target": 1,
            "type": "connected"
        }
    ]

    expected_instance_relations = [
        {
            "source": 0,
            "target": 1,
            "type": "connected"
        }
    ]

    passed = True

    if len(objects) != 3:

        passed = False

        print(
            "[ERROR] Expected 3 objects"
        )

    if len(instances) != 3:

        passed = False

        print(
            "[ERROR] Expected 3 instances"
        )

    if (
        [
            obj.num_parts
            for obj in objects
        ]
        !=
        expected_object_parts
    ):

        passed = False

        print(
            "[ERROR] Unexpected object parts"
        )

    if (
        [
            len(
                inst.points
            )
            for inst in instances
        ]
        !=
        expected_instance_points
    ):

        passed = False

        print(
            "[ERROR] Unexpected instance point counts"
        )

    if (
        canonical_relations(
            object_relations
        )
        !=
        expected_object_relations
    ):

        passed = False

        print(
            "[ERROR] Unexpected object relations"
        )

    if (
        canonical_relations(
            instance_relations
        )
        !=
        expected_instance_relations
    ):

        passed = False

        print(
            "[ERROR] Unexpected instance relations"
        )

    if passed:

        print(
            "[PASS] Base Scene"
        )

    else:

        print(
            "[FAIL] Base Scene"
        )

    return passed


# ============================================================
# Main
# ============================================================

def main():

    print()
    print(
        "=" * 60
    )
    print(
        "Struct3D v2.9 Instance-Relation Consistency"
    )
    print(
        "=" * 60
    )

    # ========================================================
    # Base
    # ========================================================

    base_points = make_scene()

    base_result = build_pipeline(
        base_points
    )

    if not validate_base_scene(
        base_result
    ):

        raise RuntimeError(
            "Base Scene Validation Failed"
        )

    # ========================================================
    # Translation
    # ========================================================

    translation = np.array(
        [
            5.0,
            -3.0,
            2.0
        ],
        dtype=float
    )

    translated_points = [

        translate(
            points,
            translation
        )

        for points in base_points
    ]

    translated_result = (
        build_pipeline(
            translated_points
        )
    )

    translation_pass = compare(
        "Translation Invariance",
        base_result,
        translated_result
    )

    # ========================================================
    # Rotation
    # ========================================================

    R = (
        rotation_matrix_z(
            np.deg2rad(
                37.0
            )
        )
        @
        rotation_matrix_y(
            np.deg2rad(
                23.0
            )
        )
        @
        rotation_matrix_x(
            np.deg2rad(
                17.0
            )
        )
    )

    rotated_points = [

        rotate(
            points,
            R
        )

        for points in base_points
    ]

    rotated_result = (
        build_pipeline(
            rotated_points
        )
    )

    rotation_pass = compare(
        "Rotation Invariance",
        base_result,
        rotated_result
    )

    # ========================================================
    # Rotation + Translation
    # ========================================================

    rotated_translated_points = [

        translate(
            rotate(
                points,
                R
            ),
            translation
        )

        for points in base_points
    ]

    rotated_translated_result = (
        build_pipeline(
            rotated_translated_points
        )
    )

    rotation_translation_pass = compare(
        "Rotation + Translation Invariance",
        base_result,
        rotated_translated_result
    )

    # ========================================================
    # Final
    # ========================================================

    all_pass = (

        translation_pass

        and

        rotation_pass

        and

        rotation_translation_pass
    )

    print()
    print(
        "=" * 60
    )

    print(
        "Struct3D v2.9"
    )

    print(
        "INSTANCE-RELATION CONSISTENCY"
    )

    print(
        "=" * 60
    )

    print(
        "Translation:",
        translation_pass
    )

    print(
        "Rotation:",
        rotation_pass
    )

    print(
        "Rotation + Translation:",
        rotation_translation_pass
    )

    print()

    if all_pass:

        print(
            "STATUS: PASS"
        )

    else:

        print(
            "STATUS: FAIL"
        )

        raise RuntimeError(
            "Struct3D v2.9 validation failed"
        )


# ============================================================
# Entry
# ============================================================

if __name__ == "__main__":

    main()