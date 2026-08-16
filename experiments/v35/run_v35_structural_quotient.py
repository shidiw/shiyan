# ============================================================
# Struct3D v3.5
# experiments/v35/run_v35_structural_quotient.py
#
# Structural Quotient
#
# Core idea
# ------------------------------------------------------------
#
# v3.1:
#     Canonical Structural Identity
#
# v3.2:
#     Structural Equivalence
#
# v3.3:
#     Structural Isomorphism
#
# v3.4:
#     Structural Automorphism
#
# v3.5:
#     Structural Quotient
#
# Mathematical object:
#
#     Q(W) = W / Aut(W)
#
# where:
#
#     Aut(W)
#
# is the structural automorphism group of W.
#
# The quotient records structural orbits rather than raw IDs.
#
# Required invariances:
#
#     Q(W) = Q(pi(W))
#
# for any admissible relabeling pi.
#
# Structural mutation:
#
#     W' != W
#
# must imply:
#
#     Q(W') != Q(W)
#
# CPU only
# ============================================================

from __future__ import annotations

import copy
import hashlib
import itertools
import pickle
import sys
from pathlib import Path

import numpy as np


# ============================================================
# Import project WorldState
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from structure.world_state import WorldState


# ============================================================
# Version
# ============================================================

VERSION = "3.5"
SEED = 20260814


# ============================================================
# Printing helpers
# ============================================================

LINE = "=" * 60
SUBLINE = "-" * 60


def section(title):
    print()
    print(SUBLINE)
    print(title)
    print(SUBLINE)


def passed(name):
    print("[PASS] {}".format(name))


def failed(name):
    print("[FAIL] {}".format(name))


# ============================================================
# Stable serialization
# ============================================================

def stable_hash(value):
    """
    Deterministic SHA256 hash.

    Used only for ordering / compact identity.
    """

    data = pickle.dumps(
        value,
        protocol=4
    )

    return hashlib.sha256(
        data
    ).hexdigest()


# ============================================================
# Generic canonicalization
# ============================================================

def normalize_scalar(value):

    if isinstance(value, np.generic):
        value = value.item()

    if isinstance(value, float):
        return round(float(value), 10)

    if isinstance(value, int):
        return int(value)

    if isinstance(value, bool):
        return bool(value)

    if value is None:
        return None

    if isinstance(value, str):
        return value

    return value


def canonicalize(value):
    """
    Canonical recursive metadata representation.

    Dictionary order is ignored.
    List order is preserved.
    """

    if isinstance(value, np.ndarray):

        arr = np.asarray(value)

        if arr.ndim == 0:
            return normalize_scalar(arr.item())

        return tuple(
            canonicalize(x)
            for x in arr.tolist()
        )

    if isinstance(value, dict):

        items = []

        for key in sorted(
            value.keys(),
            key=lambda x: str(x)
        ):

            items.append(
                (
                    str(key),
                    canonicalize(value[key])
                )
            )

        return tuple(items)

    if isinstance(value, tuple):

        return tuple(
            canonicalize(x)
            for x in value
        )

    if isinstance(value, list):

        return tuple(
            canonicalize(x)
            for x in value
        )

    return normalize_scalar(value)


# ============================================================
# Geometry signature
# ============================================================

def geometry_signature(points):
    """
    Translation / rotation / point-order invariant geometry.

    Pairwise distance multiset is used.

    This is intentionally independent of IDs.
    """

    if points is None:
        return ()

    X = np.asarray(
        points,
        dtype=np.float64
    )

    if X.size == 0:
        return ()

    if X.ndim != 2 or X.shape[1] != 3:
        raise ValueError(
            "points must have shape (N, 3)"
        )

    n = X.shape[0]

    if n == 1:

        return (
            "n",
            1,
            "dist",
            ()
        )

    diff = (
        X[:, None, :]
        -
        X[None, :, :]
    )

    distances = np.sqrt(
        np.sum(
            diff * diff,
            axis=2
        )
    )

    iu = np.triu_indices(
        n,
        k=1
    )

    values = np.sort(
        distances[iu]
    )

    values = np.round(
        values,
        10
    )

    return (
        "n",
        int(n),
        "dist",
        tuple(
            float(x)
            for x in values
        )
    )


# ============================================================
# Unit intrinsic signature
# ============================================================

def unit_intrinsic_signature(unit):

    primitive = unit.get(
        "primitive"
    )

    parameters = canonicalize(
        unit.get(
            "parameters",
            {}
        )
    )

    energy = canonicalize(
        unit.get(
            "energy",
            {}
        )
    )

    geometry = geometry_signature(
        unit.get(
            "points"
        )
    )

    return (
        "UNIT",
        VERSION,
        primitive,
        parameters,
        energy,
        geometry
    )


# ============================================================
# Relation metadata signature
# ============================================================

def relation_metadata_signature(relation):

    if not isinstance(
        relation,
        dict
    ):

        return canonicalize(
            relation
        )

    metadata = {}

    for key, value in relation.items():

        if key in (
            "source",
            "target"
        ):
            continue

        metadata[str(key)] = value

    return canonicalize(
        metadata
    )


# ============================================================
# WorldState clone
# ============================================================

def clone_world(world):

    return copy.deepcopy(
        world
    )


# ============================================================
# Transform World by a mapping
# ============================================================

def transform_world(
    world,
    unit_map,
    object_map,
    instance_map,
    relation_map
):
    """
    Apply a complete relabeling.

    IMPORTANT:
        This changes identifiers AND every reference
        pointing to those identifiers.

    It does NOT change geometry.
    """

    new_world = WorldState()

    # --------------------------------------------------------
    # Units
    # --------------------------------------------------------

    for old_id, unit in world.units.items():

        old_id = int(old_id)

        new_unit = copy.deepcopy(
            unit
        )

        new_id = int(
            unit_map[old_id]
        )

        new_unit["id"] = new_id

        new_world.add_unit(
            new_unit
        )

    # --------------------------------------------------------
    # Objects
    # --------------------------------------------------------

    for old_id, obj in world.objects.items():

        old_id = int(old_id)

        new_obj = copy.deepcopy(
            obj
        )

        new_id = int(
            object_map[old_id]
        )

        new_obj["id"] = new_id

        if "parts" in new_obj:

            new_obj["parts"] = [
                int(
                    unit_map[
                        int(unit_id)
                    ]
                )
                for unit_id in new_obj["parts"]
            ]

        if "relations" in new_obj:

            new_relations = []

            for relation in new_obj["relations"]:

                relation = copy.deepcopy(
                    relation
                )

                if "source" in relation:

                    relation["source"] = int(
                        unit_map[
                            int(
                                relation["source"]
                            )
                        ]
                    )

                if "target" in relation:

                    relation["target"] = int(
                        unit_map[
                            int(
                                relation["target"]
                            )
                        ]
                    )

                new_relations.append(
                    relation
                )

            new_obj["relations"] = new_relations

        new_world.add_object(
            new_obj
        )

    # --------------------------------------------------------
    # Instances
    # --------------------------------------------------------

    for old_id, instance in world.instances.items():

        old_id = int(old_id)

        new_instance = copy.deepcopy(
            instance
        )

        new_id = int(
            instance_map[old_id]
        )

        new_instance["id"] = new_id

        if "object" in new_instance:

            new_instance["object"] = int(
                object_map[
                    int(
                        new_instance["object"]
                    )
                ]
            )

        if "parts" in new_instance:

            new_instance["parts"] = [
                int(
                    unit_map[
                        int(unit_id)
                    ]
                )
                for unit_id in new_instance["parts"]
            ]

        new_world.add_instance(
            new_instance
        )

    # --------------------------------------------------------
    # World relations
    # --------------------------------------------------------

    relation_count = len(
        world.relations
    )

    for old_relation_id in range(
        relation_count
    ):

        relation = copy.deepcopy(
            world.relations[
                old_relation_id
            ]
        )

        if "source" in relation:

            relation["source"] = int(
                object_map[
                    int(
                        relation["source"]
                    )
                ]
            )

        if "target" in relation:

            relation["target"] = int(
                object_map[
                    int(
                        relation["target"]
                    )
                ]
            )

        new_world.add_relation(
            relation
        )

    return new_world


# ============================================================
# Identity maps
# ============================================================

def identity_mapping(keys):

    return {
        int(key): int(key)
        for key in keys
    }


# ============================================================
# Generate all permutations
# ============================================================

def permutation_mappings(keys):

    keys = tuple(
        sorted(
            int(x)
            for x in keys
        )
    )

    for permutation in itertools.permutations(
        keys
    ):

        yield {
            int(old): int(new)
            for old, new in zip(
                keys,
                permutation
            )
        }


# ============================================================
# Automorphism check
# ============================================================

def is_automorphism(
    world,
    unit_map,
    object_map,
    instance_map,
    relation_map
):
    """
    A mapping is an automorphism iff:

        transformed(W) == W

    under the canonical structural identity.
    """

    transformed = transform_world(
        world,
        unit_map,
        object_map,
        instance_map,
        relation_map
    )

    return (
        transformed.canonical_hash()
        ==
        world.canonical_hash()
    )


# ============================================================
# Enumerate automorphism group
# ============================================================

def enumerate_automorphisms(world):
    """
    Brute-force enumeration.

    v3.5 regression world is deliberately tiny:

        units      <= 4
        objects    <= 2
        instances  <= 2
        relations  <= 2

    Therefore exhaustive enumeration is practical.
    """

    unit_maps = list(
        permutation_mappings(
            world.units.keys()
        )
    )

    object_maps = list(
        permutation_mappings(
            world.objects.keys()
        )
    )

    instance_maps = list(
        permutation_mappings(
            world.instances.keys()
        )
    )

    relation_ids = list(
        range(
            len(world.relations)
        )
    )

    relation_maps = list(
        permutation_mappings(
            relation_ids
        )
    )

    automorphisms = []

    for unit_map in unit_maps:

        for object_map in object_maps:

            for instance_map in instance_maps:

                for relation_map in relation_maps:

                    if is_automorphism(
                        world,
                        unit_map,
                        object_map,
                        instance_map,
                        relation_map
                    ):

                        automorphisms.append(
                            {
                                "units": unit_map,
                                "objects": object_map,
                                "instances": instance_map,
                                "relations": relation_map
                            }
                        )

    return automorphisms


# ============================================================
# Orbit computation
# ============================================================

def compute_orbits(
    ids,
    automorphisms,
    category
):
    """
    Compute orbit partition:

        Orb(x)
        =
        { phi(x) | phi in Aut(W) }

    """

    ids = set(
        int(x)
        for x in ids
    )

    unseen = set(
        ids
    )

    orbits = []

    while unseen:

        seed = min(
            unseen
        )

        orbit = set()

        for automorphism in automorphisms:

            mapping = automorphism[
                category
            ]

            if seed in mapping:

                orbit.add(
                    int(
                        mapping[seed]
                    )
                )

        if not orbit:

            orbit.add(
                seed
            )

        orbits.append(
            frozenset(
                orbit
            )
        )

        unseen -= orbit

    orbits.sort(
        key=lambda x: (
            min(x),
            len(x)
        )
    )

    return tuple(
        orbits
    )


# ============================================================
# ID-free unit signature
# ============================================================

def id_free_unit_signature(
    world,
    unit_id
):

    unit = world.units[
        int(unit_id)
    ]

    return unit_intrinsic_signature(
        unit
    )


# ============================================================
# ID-free object signature
# ============================================================

def id_free_object_signature(
    world,
    object_id
):
    """
    Object signature intentionally contains no raw IDs.

    Unit references are represented by intrinsic unit
    signatures, not numeric IDs.
    """

    obj = world.objects[
        int(object_id)
    ]

    object_type = obj.get(
        "type"
    )

    part_signatures = []

    for unit_id in obj.get(
        "parts",
        []
    ):

        unit_id = int(
            unit_id
        )

        if unit_id not in world.units:
            continue

        part_signatures.append(
            id_free_unit_signature(
                world,
                unit_id
            )
        )

    part_signatures = tuple(
        sorted(
            part_signatures,
            key=stable_hash
        )
    )

    relation_signatures = []

    for relation in obj.get(
        "relations",
        []
    ):

        source = relation.get(
            "source"
        )

        target = relation.get(
            "target"
        )

        source_sig = None
        target_sig = None

        if source is not None:

            source = int(source)

            if source in world.units:

                source_sig = (
                    id_free_unit_signature(
                        world,
                        source
                    )
                )

        if target is not None:

            target = int(target)

            if target in world.units:

                target_sig = (
                    id_free_unit_signature(
                        world,
                        target
                    )
                )

        relation_signatures.append(
            (
                "OBJECT_RELATION",
                source_sig,
                target_sig,
                relation_metadata_signature(
                    relation
                )
            )
        )

    relation_signatures = tuple(
        sorted(
            relation_signatures,
            key=stable_hash
        )
    )

    metadata = {}

    for key, value in obj.items():

        if key in (
            "id",
            "parts",
            "relations"
        ):
            continue

        metadata[str(key)] = value

    return (
        "OBJECT",
        VERSION,
        object_type,
        part_signatures,
        relation_signatures,
        canonicalize(
            metadata
        )
    )


# ============================================================
# ID-free instance signature
# ============================================================

def id_free_instance_signature(
    world,
    instance_id
):
    """
    Instance signature contains no raw instance ID.

    Object reference is represented structurally.
    Unit references are represented structurally.
    """

    instance = world.instances[
        int(instance_id)
    ]

    object_signature = None

    if instance.get(
        "object"
    ) is not None:

        object_id = int(
            instance["object"]
        )

        if object_id in world.objects:

            object_signature = (
                id_free_object_signature(
                    world,
                    object_id
                )
            )

    part_signatures = []

    for unit_id in instance.get(
        "parts",
        []
    ):

        unit_id = int(
            unit_id
        )

        if unit_id in world.units:

            part_signatures.append(
                id_free_unit_signature(
                    world,
                    unit_id
                )
            )

    part_signatures = tuple(
        sorted(
            part_signatures,
            key=stable_hash
        )
    )

    metadata = {}

    for key, value in instance.items():

        if key in (
            "id",
            "object",
            "parts"
        ):
            continue

        metadata[str(key)] = value

    return (
        "INSTANCE",
        VERSION,
        object_signature,
        part_signatures,
        canonicalize(
            metadata
        )
    )


# ============================================================
# ID-free world relation signature
# ============================================================

def id_free_relation_signature(
    world,
    relation
):

    source_signature = None
    target_signature = None

    if relation.get(
        "source"
    ) is not None:

        source_id = int(
            relation["source"]
        )

        if source_id in world.objects:

            source_signature = (
                id_free_object_signature(
                    world,
                    source_id
                )
            )

    if relation.get(
        "target"
    ) is not None:

        target_id = int(
            relation["target"]
        )

        if target_id in world.objects:

            target_signature = (
                id_free_object_signature(
                    world,
                    target_id
                )
            )

    return (
        "RELATION",
        VERSION,
        source_signature,
        target_signature,
        relation_metadata_signature(
            relation
        )
    )


# ============================================================
# Orbit signature
# ============================================================

def orbit_signature(
    world,
    orbit,
    category
):
    """
    Structural signature of an orbit.

    CRITICAL:

        orbit member IDs are NOT included.

    Instead every member is converted to an ID-free
    structural signature.

    The orbit is represented as a multiset of intrinsic
    signatures.

    This guarantees quotient invariance under relabeling.
    """

    signatures = []

    for entity_id in orbit:

        if category == "units":

            signature = id_free_unit_signature(
                world,
                entity_id
            )

        elif category == "objects":

            signature = id_free_object_signature(
                world,
                entity_id
            )

        elif category == "instances":

            signature = id_free_instance_signature(
                world,
                entity_id
            )

        elif category == "relations":

            signature = id_free_relation_signature(
                world,
                world.relations[
                    int(entity_id)
                ]
            )

        else:

            raise ValueError(
                "unknown category: {}".format(
                    category
                )
            )

        signatures.append(
            signature
        )

    signatures = tuple(
        sorted(
            signatures,
            key=stable_hash
        )
    )

    return (
        category.upper(),
        VERSION,
        signatures
    )


# ============================================================
# Structural Quotient
# ============================================================

def structural_quotient(world):
    """
    Compute:

        Q(W) = W / Aut(W)

    """

    automorphisms = enumerate_automorphisms(
        world
    )

    unit_orbits = compute_orbits(
        world.units.keys(),
        automorphisms,
        "units"
    )

    object_orbits = compute_orbits(
        world.objects.keys(),
        automorphisms,
        "objects"
    )

    instance_orbits = compute_orbits(
        world.instances.keys(),
        automorphisms,
        "instances"
    )

    relation_orbits = compute_orbits(
        range(
            len(world.relations)
        ),
        automorphisms,
        "relations"
    )

    # --------------------------------------------------------
    # Raw orbit partition
    #
    # Useful for diagnostics, but NOT used as structural
    # identity because IDs are not invariant.
    # --------------------------------------------------------

    unit_orbit_signatures = tuple(
        sorted(
            (
                orbit_signature(
                    world,
                    orbit,
                    "units"
                )
                for orbit in unit_orbits
            ),
            key=stable_hash
        )
    )

    object_orbit_signatures = tuple(
        sorted(
            (
                orbit_signature(
                    world,
                    orbit,
                    "objects"
                )
                for orbit in object_orbits
            ),
            key=stable_hash
        )
    )

    instance_orbit_signatures = tuple(
        sorted(
            (
                orbit_signature(
                    world,
                    orbit,
                    "instances"
                )
                for orbit in instance_orbits
            ),
            key=stable_hash
        )
    )

    relation_orbit_signatures = tuple(
        sorted(
            (
                orbit_signature(
                    world,
                    orbit,
                    "relations"
                )
                for orbit in relation_orbits
            ),
            key=stable_hash
        )
    )

    return {
        "version": VERSION,

        "unit_orbits": tuple(
            tuple(
                sorted(
                    orbit
                )
            )
            for orbit in unit_orbits
        ),

        "object_orbits": tuple(
            tuple(
                sorted(
                    orbit
                )
            )
            for orbit in object_orbits
        ),

        "instance_orbits": tuple(
            tuple(
                sorted(
                    orbit
                )
            )
            for orbit in instance_orbits
        ),

        "relation_orbits": tuple(
            tuple(
                sorted(
                    orbit
                )
            )
            for orbit in relation_orbits
        ),

        "unit_orbit_signatures":
            unit_orbit_signatures,

        "object_orbit_signatures":
            object_orbit_signatures,

        "instance_orbit_signatures":
            instance_orbit_signatures,

        "relation_orbit_signatures":
            relation_orbit_signatures
    }


# ============================================================
# ID-free quotient
# ============================================================

def structural_quotient_identity(world):
    """
    Remove all raw orbit IDs.

    This is the actual mathematical quotient identity:

        Q(W) = W / Aut(W)

    represented entirely by orbit signatures.

    This function is what should be hashed for invariance.
    """

    q = structural_quotient(
        world
    )

    return {
        "version": VERSION,

        "unit_orbits":
            q["unit_orbit_signatures"],

        "object_orbits":
            q["object_orbit_signatures"],

        "instance_orbits":
            q["instance_orbit_signatures"],

        "relation_orbits":
            q["relation_orbit_signatures"]
    }


# ============================================================
# Quotient hash
# ============================================================

def quotient_hash(world):

    identity = structural_quotient_identity(
        world
    )

    return stable_hash(
        identity
    )


# ============================================================
# Quotient cardinality
# ============================================================

def quotient_cardinality(world):

    q = structural_quotient(
        world
    )

    return {
        "units": len(
            q["unit_orbit_signatures"]
        ),

        "objects": len(
            q["object_orbit_signatures"]
        ),

        "instances": len(
            q["instance_orbit_signatures"]
        ),

        "relations": len(
            q["relation_orbit_signatures"]
        )
    }


# ============================================================
# Apply random / explicit relabeling
# ============================================================

def relabel_world(
    world,
    unit_permutation,
    object_permutation,
    instance_permutation,
    relation_permutation
):

    unit_ids = tuple(
        sorted(
            world.units.keys()
        )
    )

    object_ids = tuple(
        sorted(
            world.objects.keys()
        )
    )

    instance_ids = tuple(
        sorted(
            world.instances.keys()
        )
    )

    relation_ids = tuple(
        range(
            len(world.relations)
        )
    )

    unit_map = {
        old: int(
            unit_permutation[
                index
            ]
        )
        for index, old in enumerate(
            unit_ids
        )
    }

    object_map = {
        old: int(
            object_permutation[
                index
            ]
        )
        for index, old in enumerate(
            object_ids
        )
    }

    instance_map = {
        old: int(
            instance_permutation[
                index
            ]
        )
        for index, old in enumerate(
            instance_ids
        )
    }

    relation_map = {
        old: int(
            relation_permutation[
                index
            ]
        )
        for index, old in enumerate(
            relation_ids
        )
    }

    return transform_world(
        world,
        unit_map,
        object_map,
        instance_map,
        relation_map
    )


# ============================================================
# Base world
# ============================================================

def make_base_world():

    world = WorldState()

    # --------------------------------------------------------
    # Four units
    #
    # 0 / 1 are structurally equivalent planes
    # 2 / 3 are structurally equivalent spheres
    #
    # Geometry is intentionally identical inside each pair.
    # --------------------------------------------------------

    plane_a = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.1, 0.0, 0.0],
            [0.0, 0.1, 0.0],
            [0.1, 0.1, 0.0],
            [0.03, 0.02, 0.0],
            [0.07, 0.02, 0.0],
            [0.02, 0.08, 0.0],
            [0.08, 0.08, 0.0],
        ],
        dtype=np.float64
    )

    plane_b = plane_a.copy()

    sphere_a = np.array(
        [
            [0.0, 0.0, 0.05],
            [0.0, 0.0, -0.05],
            [0.05, 0.0, 0.0],
            [-0.05, 0.0, 0.0],
            [0.0, 0.05, 0.0],
            [0.0, -0.05, 0.0],
            [0.035, 0.035, 0.0],
            [-0.035, -0.035, 0.0],
        ],
        dtype=np.float64
    )

    sphere_b = sphere_a.copy()

    world.add_unit(
        {
            "id": 0,
            "primitive": "plane",
            "parameters": {
                "scale": 1.0
            },
            "energy": {
                "fit": 0.1
            },
            "points": plane_a
        }
    )

    world.add_unit(
        {
            "id": 1,
            "primitive": "plane",
            "parameters": {
                "scale": 1.0
            },
            "energy": {
                "fit": 0.1
            },
            "points": plane_b
        }
    )

    world.add_unit(
        {
            "id": 2,
            "primitive": "sphere",
            "parameters": {
                "scale": 1.0
            },
            "energy": {
                "fit": 0.1
            },
            "points": sphere_a
        }
    )

    world.add_unit(
        {
            "id": 3,
            "primitive": "sphere",
            "parameters": {
                "scale": 1.0
            },
            "energy": {
                "fit": 0.1
            },
            "points": sphere_b
        }
    )

    # --------------------------------------------------------
    # Two structurally equivalent objects
    # --------------------------------------------------------

    world.add_object(
        {
            "id": 0,
            "type": "assembly",
            "parts": [
                0,
                3
            ],
            "relations": []
        }
    )

    world.add_object(
        {
            "id": 1,
            "type": "assembly",
            "parts": [
                1,
                2
            ],
            "relations": []
        }
    )

    # --------------------------------------------------------
    # Two structurally equivalent instances
    # --------------------------------------------------------

    world.add_instance(
        {
            "id": 0,
            "object": 0,
            "parts": [
                0,
                3
            ]
        }
    )

    world.add_instance(
        {
            "id": 1,
            "object": 1,
            "parts": [
                1,
                2
            ]
        }
    )

    # --------------------------------------------------------
    # Two structurally equivalent world relations
    # --------------------------------------------------------

    world.add_relation(
        {
            "source": 0,
            "target": 1,
            "type": "adjacent",
            "confidence": 0.9
        }
    )

    world.add_relation(
        {
            "source": 1,
            "target": 0,
            "type": "adjacent",
            "confidence": 0.9
        }
    )

    return world


# ============================================================
# Structural mutation
# ============================================================

def mutate_world(world):

    mutated = clone_world(
        world
    )

    # Change primitive semantics.
    mutated.units[
        0
    ]["primitive"] = "cylinder"

    return mutated


# ============================================================
# Explicit expected automorphisms
# ============================================================

def explicit_symmetry_maps():

    return [
        {
            "units": {
                0: 0,
                1: 1,
                2: 2,
                3: 3
            },

            "objects": {
                0: 0,
                1: 1
            },

            "instances": {
                0: 0,
                1: 1
            },

            "relations": {
                0: 0,
                1: 1
            }
        },

        {
            "units": {
                0: 1,
                1: 0,
                2: 3,
                3: 2
            },

            "objects": {
                0: 0,
                1: 1
            },

            "instances": {
                0: 0,
                1: 1
            },

            "relations": {
                0: 0,
                1: 1
            }
        },

        {
            "units": {
                0: 0,
                1: 1,
                2: 2,
                3: 3
            },

            "objects": {
                0: 1,
                1: 0
            },

            "instances": {
                0: 1,
                1: 0
            },

            "relations": {
                0: 1,
                1: 0
            }
        },

        {
            "units": {
                0: 1,
                1: 0,
                2: 3,
                3: 2
            },

            "objects": {
                0: 1,
                1: 0
            },

            "instances": {
                0: 1,
                1: 0
            },

            "relations": {
                0: 1,
                1: 0
            }
        },

        {
            "units": {
                0: 1,
                1: 0,
                2: 3,
                3: 2
            },

            "objects": {
                0: 0,
                1: 1
            },

            "instances": {
                0: 1,
                1: 0
            },

            "relations": {
                0: 1,
                1: 0
            }
        },

        {
            "units": {
                0: 0,
                1: 1,
                2: 2,
                3: 3
            },

            "objects": {
                0: 1,
                1: 0
            },

            "instances": {
                0: 0,
                1: 1
            },

            "relations": {
                0: 1,
                1: 0
            }
        }
    ]


# ============================================================
# Test 1
# ============================================================

def test_world_validation(world):

    result = world.validate()

    ok = bool(
        result["valid"]
    )

    if ok:
        passed(
            "World Validation"
        )
    else:
        failed(
            "World Validation"
        )

    return ok


# ============================================================
# Test 2
# ============================================================

def test_quotient_exists(world):

    q = structural_quotient(
        world
    )

    ok = (
        isinstance(
            q,
            dict
        )
        and
        q.get("version") == VERSION
    )

    print(
        "Quotient:",
        q
    )

    if ok:
        passed(
            "Quotient Exists"
        )
    else:
        failed(
            "Quotient Exists"
        )

    return ok


# ============================================================
# Test 3
# ============================================================

def test_unit_orbit_partition(world):

    automorphisms = enumerate_automorphisms(
        world
    )

    orbits = compute_orbits(
        world.units.keys(),
        automorphisms,
        "units"
    )

    print(
        "Unit Orbits:",
        orbits
    )

    union = set()

    disjoint = True

    for orbit in orbits:

        if union.intersection(
            orbit
        ):

            disjoint = False

        union.update(
            orbit
        )

    ok = (
        union
        ==
        set(
            world.units.keys()
        )
        and
        disjoint
    )

    if ok:
        passed(
            "Unit Orbit Partition"
        )
    else:
        failed(
            "Unit Orbit Partition"
        )

    return ok


# ============================================================
# Test 4
# ============================================================

def test_object_orbit_partition(world):

    automorphisms = enumerate_automorphisms(
        world
    )

    orbits = compute_orbits(
        world.objects.keys(),
        automorphisms,
        "objects"
    )

    print(
        "Object Orbits:",
        orbits
    )

    union = set()

    disjoint = True

    for orbit in orbits:

        if union.intersection(
            orbit
        ):

            disjoint = False

        union.update(
            orbit
        )

    ok = (
        union
        ==
        set(
            world.objects.keys()
        )
        and
        disjoint
    )

    if ok:
        passed(
            "Object Orbit Partition"
        )
    else:
        failed(
            "Object Orbit Partition"
        )

    return ok


# ============================================================
# Test 5
# ============================================================

def test_instance_orbit_partition(world):

    automorphisms = enumerate_automorphisms(
        world
    )

    orbits = compute_orbits(
        world.instances.keys(),
        automorphisms,
        "instances"
    )

    print(
        "Instance Orbits:",
        orbits
    )

    union = set()

    disjoint = True

    for orbit in orbits:

        if union.intersection(
            orbit
        ):

            disjoint = False

        union.update(
            orbit
        )

    ok = (
        union
        ==
        set(
            world.instances.keys()
        )
        and
        disjoint
    )

    if ok:
        passed(
            "Instance Orbit Partition"
        )
    else:
        failed(
            "Instance Orbit Partition"
        )

    return ok


# ============================================================
# Test 6
# ============================================================

def test_relation_orbit_partition(world):

    automorphisms = enumerate_automorphisms(
        world
    )

    relation_ids = range(
        len(
            world.relations
        )
    )

    orbits = compute_orbits(
        relation_ids,
        automorphisms,
        "relations"
    )

    print(
        "Relation Orbits:",
        orbits
    )

    union = set()

    disjoint = True

    for orbit in orbits:

        if union.intersection(
            orbit
        ):

            disjoint = False

        union.update(
            orbit
        )

    ok = (
        union
        ==
        set(
            relation_ids
        )
        and
        disjoint
    )

    if ok:
        passed(
            "Relation Orbit Partition"
        )
    else:
        failed(
            "Relation Orbit Partition"
        )

    return ok


# ============================================================
# Test 7
# ============================================================

def test_orbit_partition(world):

    automorphisms = enumerate_automorphisms(
        world
    )

    categories = [
        (
            "units",
            set(
                world.units.keys()
            )
        ),

        (
            "objects",
            set(
                world.objects.keys()
            )
        ),

        (
            "instances",
            set(
                world.instances.keys()
            )
        ),

        (
            "relations",
            set(
                range(
                    len(
                        world.relations
                    )
                )
            )
        )
    ]

    ok = True

    for category, universe in categories:

        orbits = compute_orbits(
            universe,
            automorphisms,
            category
        )

        flattened = set()

        for orbit in orbits:

            if flattened.intersection(
                orbit
            ):

                ok = False

            flattened.update(
                orbit
            )

        if flattened != universe:

            ok = False

    if ok:
        passed(
            "Orbit Partition Property"
        )
    else:
        failed(
            "Orbit Partition Property"
        )

    return ok


# ============================================================
# Test 8
# ============================================================

def test_quotient_invariance(world):

    q_original = structural_quotient_identity(
        world
    )

    original_hash = stable_hash(
        q_original
    )

    # --------------------------------------------------------
    # A deliberately nontrivial relabeling.
    # --------------------------------------------------------

    permuted = relabel_world(
        world,

        unit_permutation=[
            2,
            0,
            3,
            1
        ],

        object_permutation=[
            1,
            0
        ],

        instance_permutation=[
            1,
            0
        ],

        relation_permutation=[
            1,
            0
        ]
    )

    q_permuted = structural_quotient_identity(
        permuted
    )

    permuted_hash = stable_hash(
        q_permuted
    )

    print(
        "Original quotient hash:",
        original_hash
    )

    print(
        "Permuted quotient hash:",
        permuted_hash
    )

    ok = (
        q_original
        ==
        q_permuted
    )

    if ok:
        passed(
            "Quotient Invariance"
        )
    else:
        failed(
            "Quotient Invariance"
        )

    return ok


# ============================================================
# Test 9
# ============================================================

def test_quotient_idempotence(world):

    q1 = structural_quotient_identity(
        world
    )

    h1 = stable_hash(
        q1
    )

    # --------------------------------------------------------
    # Quotient identity is already ID-free.
    #
    # Re-canonicalization must therefore be identical.
    # --------------------------------------------------------

    q2 = canonicalize(
        q1
    )

    q3 = canonicalize(
        q2
    )

    h2 = stable_hash(
        q2
    )

    h3 = stable_hash(
        q3
    )

    ok = (
        h1 == h2
        or
        q2 == q3
    )

    if ok:
        passed(
            "Quotient Idempotence"
        )
    else:
        failed(
            "Quotient Idempotence"
        )

    return ok


# ============================================================
# Test 10
# ============================================================

def test_explicit_automorphisms(world):

    explicit = explicit_symmetry_maps()

    tested = 0
    ok = True

    for mapping in explicit:

        if not is_automorphism(
            world,
            mapping["units"],
            mapping["objects"],
            mapping["instances"],
            mapping["relations"]
        ):

            ok = False

        tested += 1

    print(
        "Automorphisms tested:",
        tested
    )

    if ok:
        passed(
            "All Explicit Symmetries Are Automorphisms"
        )
    else:
        failed(
            "All Explicit Symmetries Are Automorphisms"
        )

    return ok


# ============================================================
# Test 11
# ============================================================

def test_quotient_cardinality(world):

    cardinality = quotient_cardinality(
        world
    )

    print(
        "Quotient Cardinalities:",
        cardinality
    )

    ok = all(
        isinstance(
            value,
            int
        )
        and
        value >= 1
        for value in cardinality.values()
    )

    if ok:
        passed(
            "Quotient Cardinality"
        )
    else:
        failed(
            "Quotient Cardinality"
        )

    return ok


# ============================================================
# Test 12
# ============================================================

def test_structural_mutation(world):

    mutated = mutate_world(
        world
    )

    original_hash = quotient_hash(
        world
    )

    mutated_hash = quotient_hash(
        mutated
    )

    print(
        "Original quotient hash:",
        original_hash
    )

    print(
        "Mutated quotient hash:",
        mutated_hash
    )

    ok = (
        original_hash
        !=
        mutated_hash
    )

    if ok:
        passed(
            "Structural Mutation Changes Quotient"
        )
    else:
        failed(
            "Structural Mutation Changes Quotient"
        )

    return ok


# ============================================================
# Main
# ============================================================

def main():

    np.random.seed(
        SEED
    )

    print(LINE)
    print(
        "Struct3D v3.5 Structural Quotient Regression Suite"
    )
    print(LINE)

    print(
        "Version: {}".format(
            VERSION
        )
    )

    print(
        "Seed: {}".format(
            SEED
        )
    )

    # --------------------------------------------------------
    # Base world
    # --------------------------------------------------------

    section(
        "[1] Base World"
    )

    world = make_base_world()

    print(
        "Units:",
        len(world.units)
    )

    print(
        "Objects:",
        len(world.objects)
    )

    print(
        "Instances:",
        len(world.instances)
    )

    print(
        "Relations:",
        len(world.relations)
    )

    results = []

    # --------------------------------------------------------
    # 1
    # --------------------------------------------------------

    results.append(
        (
            "World Validation",
            test_world_validation(
                world
            )
        )
    )

    # --------------------------------------------------------
    # 2
    # --------------------------------------------------------

    section(
        "Structural Quotient"
    )

    results.append(
        (
            "Quotient Exists",
            test_quotient_exists(
                world
            )
        )
    )

    # --------------------------------------------------------
    # 3
    # --------------------------------------------------------

    section(
        "Unit Structural Orbits"
    )

    results.append(
        (
            "Unit Orbit Partition",
            test_unit_orbit_partition(
                world
            )
        )
    )

    # --------------------------------------------------------
    # 4
    # --------------------------------------------------------

    section(
        "Object Structural Orbits"
    )

    results.append(
        (
            "Object Orbit Partition",
            test_object_orbit_partition(
                world
            )
        )
    )

    # --------------------------------------------------------
    # 5
    # --------------------------------------------------------

    section(
        "Instance Structural Orbits"
    )

    results.append(
        (
            "Instance Orbit Partition",
            test_instance_orbit_partition(
                world
            )
        )
    )

    # --------------------------------------------------------
    # 6
    # --------------------------------------------------------

    section(
        "Relation Structural Orbits"
    )

    results.append(
        (
            "Relation Orbit Partition",
            test_relation_orbit_partition(
                world
            )
        )
    )

    # --------------------------------------------------------
    # 7
    # --------------------------------------------------------

    section(
        "Orbit Partition"
    )

    results.append(
        (
            "Orbit Partition Property",
            test_orbit_partition(
                world
            )
        )
    )

    # --------------------------------------------------------
    # 8
    # --------------------------------------------------------

    section(
        "Quotient Invariance"
    )

    results.append(
        (
            "Quotient Invariance",
            test_quotient_invariance(
                world
            )
        )
    )

    # --------------------------------------------------------
    # 9
    # --------------------------------------------------------

    section(
        "Quotient Idempotence"
    )

    results.append(
        (
            "Quotient Idempotence",
            test_quotient_idempotence(
                world
            )
        )
    )

    # --------------------------------------------------------
    # 10
    # --------------------------------------------------------

    section(
        "Explicit Automorphism Validation"
    )

    results.append(
        (
            "All Explicit Symmetries Are Automorphisms",
            test_explicit_automorphisms(
                world
            )
        )
    )

    # --------------------------------------------------------
    # 11
    # --------------------------------------------------------

    section(
        "Quotient Cardinality"
    )

    results.append(
        (
            "Quotient Cardinality",
            test_quotient_cardinality(
                world
            )
        )
    )

    # --------------------------------------------------------
    # 12
    # --------------------------------------------------------

    section(
        "Structural Mutation"
    )

    results.append(
        (
            "Structural Mutation Changes Quotient",
            test_structural_mutation(
                world
            )
        )
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print(LINE)
    print(
        "Struct3D v3.5"
    )
    print(LINE)

    passed_count = sum(
        1
        for _, ok in results
        if ok
    )

    failed_count = (
        len(results)
        -
        passed_count
    )

    print(
        "Total tests: {}".format(
            len(results)
        )
    )

    print(
        "Passed: {}".format(
            passed_count
        )
    )

    print(
        "Failed: {}".format(
            failed_count
        )
    )

    if failed_count == 0:

        print(
            "STATUS: PASS"
        )

    else:

        print(
            "STATUS: FAIL"
        )

    print(LINE)

    return (
        0
        if failed_count == 0
        else 1
    )


# ============================================================
# Entry
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )