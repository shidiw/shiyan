# ============================================================
# Struct3D v3.3
# structure/structural_isomorphism.py
#
# Structural Isomorphism
#
# Core principle
# ------------------------------------------------------------
#
# W1 ≅S W2
#
# iff there exist structure-preserving bijections:
#
#     φU : U1 -> U2
#     φO : O1 -> O2
#     φI : I1 -> I2
#
# preserving:
#
#     primitive
#     parameters
#     energy
#     object composition
#     instance composition
#     relation topology
#     relation semantics
#     relation confidence
#
# IDs are NEVER structural identity.
#
# CPU only
# ============================================================

from __future__ import annotations

import copy
import hashlib
import pickle

import numpy as np


# ============================================================
# Version
# ============================================================

STRUCTURAL_ISOMORPHISM_VERSION = "3.3"


# ============================================================
# Deterministic serialization
# ============================================================

def _stable_hash(value):

    data = pickle.dumps(
        value,
        protocol=4
    )

    return hashlib.sha256(
        data
    ).hexdigest()


# ============================================================
# Value normalization
# ============================================================

def _normalize_value(value):

    if isinstance(value, np.generic):
        return value.item()

    if isinstance(value, np.ndarray):
        return tuple(
            _normalize_value(x)
            for x in value.tolist()
        )

    if isinstance(value, dict):

        return tuple(
            (
                str(k),
                _normalize_value(v)
            )
            for k, v in sorted(
                value.items(),
                key=lambda x: str(x[0])
            )
        )

    if isinstance(value, list):

        return tuple(
            _normalize_value(x)
            for x in value
        )

    if isinstance(value, tuple):

        return tuple(
            _normalize_value(x)
            for x in value
        )

    return value


# ============================================================
# Unit invariant
# ============================================================

def unit_invariant(unit):

    return (
        "UNIT",
        unit.get("primitive"),
        _normalize_value(
            unit.get("parameters", {})
        ),
        _normalize_value(
            unit.get("energy", {})
        )
    )


# ============================================================
# Object invariant
# ============================================================

def object_invariant(obj):

    return (
        "OBJECT",
        obj.get("type"),
        len(
            obj.get("parts", [])
        ),
        len(
            obj.get("relations", [])
        )
    )


# ============================================================
# Instance invariant
# ============================================================

def instance_invariant(instance):

    return (
        "INSTANCE",
        instance.get("object") is not None,
        len(
            instance.get("parts", [])
        )
    )


# ============================================================
# Relation invariant
# ============================================================

def relation_invariant(relation):

    return (
        relation.get("type"),
        relation.get("confidence")
    )


# ============================================================
# Build unit adjacency
# ============================================================

def _object_unit_relation_signature(
    obj,
    unit_map
):

    relations = []

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

        source = unit_map.get(
            source
        )

        target = unit_map.get(
            target
        )

        relations.append(
            (
                source,
                target,
                relation.get("type"),
                relation.get("confidence")
            )
        )

    return tuple(
        sorted(
            relations,
            key=_stable_hash
        )
    )


# ============================================================
# Structural fingerprint
# ============================================================

def world_fingerprint(world):

    units = []

    for unit in world.units.values():

        units.append(
            unit_invariant(unit)
        )

    units = tuple(
        sorted(
            units,
            key=_stable_hash
        )
    )

    objects = []

    for obj in world.objects.values():

        objects.append(
            object_invariant(obj)
        )

    objects = tuple(
        sorted(
            objects,
            key=_stable_hash
        )
    )

    instances = []

    for instance in world.instances.values():

        instances.append(
            instance_invariant(instance)
        )

    instances = tuple(
        sorted(
            instances,
            key=_stable_hash
        )
    )

    relations = []

    for relation in world.relations:

        relations.append(
            relation_invariant(
                relation
            )
        )

    relations = tuple(
        sorted(
            relations,
            key=_stable_hash
        )
    )

    return (
        "STRUCTURAL_FINGERPRINT",
        STRUCTURAL_ISOMORPHISM_VERSION,
        len(world.units),
        units,
        len(world.objects),
        objects,
        len(world.instances),
        instances,
        len(world.relations),
        relations
    )


# ============================================================
# Candidate mapping
# ============================================================

def _candidate_units(
    world_a,
    world_b
):

    groups_a = {}
    groups_b = {}

    for uid, unit in world_a.units.items():

        key = unit_invariant(unit)

        groups_a.setdefault(
            key,
            []
        ).append(uid)

    for uid, unit in world_b.units.items():

        key = unit_invariant(unit)

        groups_b.setdefault(
            key,
            []
        ).append(uid)

    return groups_a, groups_b


# ============================================================
# Relation consistency
# ============================================================

def _relations_consistent(
    world_a,
    world_b,
    object_map
):

    relations_a = []

    for relation in world_a.relations:

        source = relation.get(
            "source"
        )

        target = relation.get(
            "target"
        )

        mapped_source = object_map.get(
            source
        )

        mapped_target = object_map.get(
            target
        )

        relations_a.append(
            (
                mapped_source,
                mapped_target,
                relation.get("type"),
                relation.get("confidence")
            )
        )

    relations_b = []

    for relation in world_b.relations:

        relations_b.append(
            (
                relation.get("source"),
                relation.get("target"),
                relation.get("type"),
                relation.get("confidence")
            )
        )

    return (
        sorted(
            relations_a,
            key=_stable_hash
        )
        ==
        sorted(
            relations_b,
            key=_stable_hash
        )
    )


# ============================================================
# Object consistency
# ============================================================

def _object_consistent(
    obj_a,
    obj_b,
    unit_map
):

    if obj_a.get("type") != obj_b.get("type"):
        return False

    parts_a = sorted(
        unit_map.get(
            int(uid)
        )
        for uid in obj_a.get(
            "parts",
            []
        )
    )

    parts_b = sorted(
        int(uid)
        for uid in obj_b.get(
            "parts",
            []
        )
    )

    if parts_a != parts_b:
        return False

    relations_a = []

    for relation in obj_a.get(
        "relations",
        []
    ):

        source = relation.get(
            "source"
        )

        target = relation.get(
            "target"
        )

        relations_a.append(
            (
                unit_map.get(
                    int(source)
                ),
                unit_map.get(
                    int(target)
                ),
                relation.get("type"),
                relation.get("confidence")
            )
        )

    relations_b = []

    for relation in obj_b.get(
        "relations",
        []
    ):

        relations_b.append(
            (
                int(
                    relation.get("source")
                ),
                int(
                    relation.get("target")
                ),
                relation.get("type"),
                relation.get("confidence")
            )
        )

    return (
        sorted(
            relations_a,
            key=_stable_hash
        )
        ==
        sorted(
            relations_b,
            key=_stable_hash
        )
    )


# ============================================================
# Backtracking
# ============================================================

def _search_unit_mapping(
    world_a,
    world_b,
    mapping,
    used
):

    if len(mapping) == len(
        world_a.units
    ):
        return mapping

    remaining = [
        uid
        for uid in world_a.units
        if uid not in mapping
    ]

    uid_a = min(
        remaining,
        key=lambda x: len(
            [
                y
                for y in world_b.units
                if y not in used
                and
                unit_invariant(
                    world_a.units[x]
                )
                ==
                unit_invariant(
                    world_b.units[y]
                )
            ]
        )
    )

    invariant = unit_invariant(
        world_a.units[uid_a]
    )

    candidates = [

        uid_b

        for uid_b in world_b.units

        if uid_b not in used

        and
        unit_invariant(
            world_b.units[uid_b]
        )
        ==
        invariant
    ]

    for uid_b in candidates:

        mapping[uid_a] = uid_b
        used.add(uid_b)

        if _partial_object_consistency(
            world_a,
            world_b,
            mapping
        ):

            result = _search_unit_mapping(
                world_a,
                world_b,
                mapping,
                used
            )

            if result is not None:
                return result

        used.remove(uid_b)
        del mapping[uid_a]

    return None


# ============================================================
# Partial object consistency
# ============================================================

def _partial_object_consistency(
    world_a,
    world_b,
    unit_map
):

    for obj_a in world_a.objects.values():

        mapped_parts = [

            unit_map[int(uid)]

            for uid in obj_a.get(
                "parts",
                []
            )

            if int(uid) in unit_map
        ]

        if not mapped_parts:
            continue

        matched = False

        for obj_b in world_b.objects.values():

            if obj_a.get("type") != obj_b.get("type"):
                continue

            parts_b = set(
                int(uid)
                for uid in obj_b.get(
                    "parts",
                    []
                )
            )

            if set(mapped_parts).issubset(
                parts_b
            ):

                matched = True
                break

        if not matched:
            return False

    return True


# ============================================================
# Full object mapping
# ============================================================

def _build_object_mapping(
    world_a,
    world_b,
    unit_map
):

    candidates = {}

    for oid_a, obj_a in world_a.objects.items():

        candidates[oid_a] = []

        for oid_b, obj_b in world_b.objects.items():

            if _object_consistent(
                obj_a,
                obj_b,
                unit_map
            ):

                candidates[oid_a].append(
                    oid_b
                )

        if not candidates[oid_a]:
            return None

    ordered = sorted(
        candidates,
        key=lambda oid: len(
            candidates[oid]
        )
    )

    mapping = {}
    used = set()

    def search(index):

        if index == len(ordered):
            return True

        oid_a = ordered[index]

        for oid_b in candidates[oid_a]:

            if oid_b in used:
                continue

            mapping[oid_a] = oid_b
            used.add(oid_b)

            if search(index + 1):
                return True

            used.remove(oid_b)
            del mapping[oid_a]

        return False

    if not search(0):
        return None

    return mapping


# ============================================================
# Instance mapping
# ============================================================

def _instances_consistent(
    world_a,
    world_b,
    object_map,
    unit_map
):

    candidates = {}

    for iid_a, instance_a in world_a.instances.items():

        candidates[iid_a] = []

        for iid_b, instance_b in world_b.instances.items():

            object_a = instance_a.get(
                "object"
            )

            object_b = instance_b.get(
                "object"
            )

            if object_a is not None:

                if object_map.get(
                    int(object_a)
                ) != int(object_b):

                    continue

            parts_a = sorted(

                unit_map.get(
                    int(uid)
                )

                for uid in instance_a.get(
                    "parts",
                    []
                )

                if int(uid) in unit_map
            )

            parts_b = sorted(

                int(uid)

                for uid in instance_b.get(
                    "parts",
                    []
                )
            )

            if parts_a != parts_b:
                continue

            candidates[iid_a].append(
                iid_b
            )

        if not candidates[iid_a]:
            return False

    ordered = sorted(
        candidates,
        key=lambda iid: len(
            candidates[iid]
        )
    )

    used = set()

    def search(index):

        if index == len(ordered):
            return True

        iid_a = ordered[index]

        for iid_b in candidates[iid_a]:

            if iid_b in used:
                continue

            used.add(iid_b)

            if search(index + 1):
                return True

            used.remove(iid_b)

        return False

    return search(0)


# ============================================================
# Main API
# ============================================================

def structural_isomorphic(
    world_a,
    world_b
):

    # --------------------------------------------------------
    # Cardinality
    # --------------------------------------------------------

    if len(world_a.units) != len(world_b.units):
        return False

    if len(world_a.objects) != len(world_b.objects):
        return False

    if len(world_a.instances) != len(world_b.instances):
        return False

    if len(world_a.relations) != len(world_b.relations):
        return False

    # --------------------------------------------------------
    # Fast fingerprint rejection
    # --------------------------------------------------------

    fingerprint_a = world_fingerprint(
        world_a
    )

    fingerprint_b = world_fingerprint(
        world_b
    )

    if (
        len(fingerprint_a)
        !=
        len(fingerprint_b)
    ):
        return False

    # --------------------------------------------------------
    # Unit mapping
    # --------------------------------------------------------

    unit_map = _search_unit_mapping(
        world_a,
        world_b,
        {},
        set()
    )

    if unit_map is None:
        return False

    # --------------------------------------------------------
    # Object mapping
    # --------------------------------------------------------

    object_map = _build_object_mapping(
        world_a,
        world_b,
        unit_map
    )

    if object_map is None:
        return False

    # --------------------------------------------------------
    # World relations
    # --------------------------------------------------------

    if not _relations_consistent(
        world_a,
        world_b,
        object_map
    ):
        return False

    # --------------------------------------------------------
    # Instances
    # --------------------------------------------------------

    if not _instances_consistent(
        world_a,
        world_b,
        object_map,
        unit_map
    ):
        return False

    return True


# ============================================================
# End
# ============================================================