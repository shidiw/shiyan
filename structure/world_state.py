# ============================================================
# Struct3D v3.2
# structure/world_state.py
#
# Canonical World State
#
# Core principle
# ------------------------------------------------------------
#
# IDs are references, NOT structural identity.
#
# Canonical identity must satisfy:
#
#     rigid(world) == world
#     permutation(world) == world
#     dictionary_reorder(world) == world
#
# while:
#
#     structural_mutation(world) != world
#
# v3.2 adds:
#
#     Numerical canonicalization
#     Rigid-transform floating-point tolerance
#
# CPU only
# ============================================================

from __future__ import annotations

import copy
import hashlib
import math
import pickle

import numpy as np


# ============================================================
# Version
# ============================================================

WORLD_STATE_VERSION = "3.2"


# ============================================================
# Numerical Canonicalization
# ============================================================

CANONICAL_GEOMETRY_TOLERANCE = 1e-8


def _quantize_float(
    value,
    tolerance=CANONICAL_GEOMETRY_TOLERANCE
):
    """
    Deterministic numerical quantization.

    Floating-point implementations of mathematically identical
    rigid transformations can introduce tiny numerical errors.

    Example:

        d(X)      = 1.7974090619...
        d(RX)     = 1.79740906190000...

    These values represent the same geometric quantity but may
    differ in their final floating-point digits.

    Quantization maps values inside the admissible numerical
    tolerance to a common canonical representation.
    """

    value = float(value)

    if not math.isfinite(value):
        return str(value)

    return float(
        np.round(
            value / tolerance
        ) * tolerance
    )


# ============================================================
# Helpers
# ============================================================

def _normalize_scalar(value):
    """
    Convert numpy scalars into deterministic Python scalars.
    """

    if isinstance(
        value,
        np.generic
    ):
        value = value.item()

    if isinstance(
        value,
        float
    ):

        if not math.isfinite(value):
            return str(value)

        return _quantize_float(
            value
        )

    if isinstance(
        value,
        int
    ):
        return int(value)

    if isinstance(
        value,
        bool
    ):
        return bool(value)

    if value is None:
        return None

    if isinstance(
        value,
        str
    ):
        return value

    return value


def _canonicalize_value(value):
    """
    Recursively canonicalize arbitrary metadata.

    Dictionary ordering is removed.

    Lists remain ordered unless the caller explicitly sorts
    them because list ordering may itself be structural.
    """

    if isinstance(
        value,
        np.ndarray
    ):

        arr = np.asarray(
            value
        )

        if arr.ndim == 0:

            return _normalize_scalar(
                arr.item()
            )

        return [
            _canonicalize_value(
                x
            )
            for x in arr.tolist()
        ]

    if isinstance(
        value,
        dict
    ):

        result = {}

        for key in sorted(
            value.keys(),
            key=lambda x: str(x)
        ):

            result[str(key)] = (
                _canonicalize_value(
                    value[key]
                )
            )

        return result

    if isinstance(
        value,
        tuple
    ):

        return tuple(
            _canonicalize_value(
                x
            )
            for x in value
        )

    if isinstance(
        value,
        list
    ):

        return [
            _canonicalize_value(
                x
            )
            for x in value
        ]

    return _normalize_scalar(
        value
    )


def _stable_pickle_hash(value):
    """
    Deterministic hash used internally for structural sorting.
    """

    payload = pickle.dumps(
        value,
        protocol=4
    )

    return hashlib.sha256(
        payload
    ).hexdigest()


# ============================================================
# Geometry Canonicalization
# ============================================================

def _canonical_points(points):
    """
    Geometry descriptor invariant to:

        1. translation
        2. rotation
        3. point ordering
        4. floating-point perturbation

    The descriptor is based on the complete multiset of
    pairwise distances.

    Raw coordinates are NEVER stored in the canonical
    structural identity.

    Therefore:

        X
        RX + t
        permutation(X)

    produce the same geometric descriptor, up to the defined
    numerical tolerance.
    """

    # --------------------------------------------------------
    # Empty geometry
    # --------------------------------------------------------

    if points is None:

        return ()

    X = np.asarray(
        points,
        dtype=np.float64
    )

    if X.size == 0:

        return ()

    # --------------------------------------------------------
    # Shape validation
    # --------------------------------------------------------

    if (
        X.ndim != 2
        or X.shape[1] != 3
    ):

        raise ValueError(
            "points must have shape (N, 3)"
        )

    # --------------------------------------------------------
    # Remove translation
    # --------------------------------------------------------

    X = (
        X
        -
        np.mean(
            X,
            axis=0,
            keepdims=True
        )
    )

    n = X.shape[0]

    # --------------------------------------------------------
    # Single point
    # --------------------------------------------------------

    if n == 1:

        return (
            "n",
            1,
            "dist",
            ()
        )

    # --------------------------------------------------------
    # Pairwise displacement
    # --------------------------------------------------------

    diff = (
        X[:, None, :]
        -
        X[None, :, :]
    )

    # --------------------------------------------------------
    # Pairwise Euclidean distance
    # --------------------------------------------------------

    distances = np.sqrt(
        np.sum(
            diff * diff,
            axis=2
        )
    )

    # --------------------------------------------------------
    # Upper triangle
    # --------------------------------------------------------

    iu = np.triu_indices(
        n,
        k=1
    )

    values = distances[iu]

    # --------------------------------------------------------
    # Numerical canonicalization
    #
    # This is the key v3.2 fix.
    #
    # Do NOT allow raw floating-point values to determine
    # structural identity.
    # --------------------------------------------------------

    values = np.asarray(
        [
            _quantize_float(
                value
            )
            for value in values
        ],
        dtype=np.float64
    )

    # --------------------------------------------------------
    # Remove point ordering
    # --------------------------------------------------------

    values = np.sort(
        values
    )

    # --------------------------------------------------------
    # Immutable canonical representation
    # --------------------------------------------------------

    return (
        "n",
        int(n),
        "dist",
        tuple(
            float(value)
            for value in values
        )
    )


# ============================================================
# Unit Structural Signature
# ============================================================

def _unit_signature(unit):
    """
    Structural identity of one unit.

    IMPORTANT:

        unit["id"] is intentionally excluded.
    """

    if not isinstance(
        unit,
        dict
    ):

        raise TypeError(
            "unit must be a dictionary"
        )

    primitive = unit.get(
        "primitive"
    )

    parameters = _canonicalize_value(
        unit.get(
            "parameters",
            {}
        )
    )

    energy = _canonicalize_value(
        unit.get(
            "energy",
            {}
        )
    )

    geometry = _canonical_points(
        unit.get(
            "points"
        )
    )

    return (
        "UNIT",
        WORLD_STATE_VERSION,
        primitive,
        parameters,
        energy,
        geometry
    )


# ============================================================
# Unit Key
# ============================================================

def _unit_key(unit):
    """
    Stable sorting key for units.

    Raw unit ID is NEVER used.
    """

    signature = _unit_signature(
        unit
    )

    return (
        _stable_pickle_hash(
            signature
        ),
        signature
    )


# ============================================================
# Unit Canonical Table
# ============================================================

def _canonical_unit_table(
    units
):
    """
    Returns:

        canonical_units
        raw_id -> canonical_id

    Canonical IDs are assigned from structural signatures,
    never from original IDs.
    """

    records = []

    for raw_id, unit in units.items():

        signature = _unit_signature(
            unit
        )

        records.append(
            (
                signature,
                int(raw_id),
                unit
            )
        )

    # --------------------------------------------------------
    # Structural ordering
    #
    # Raw ID is deliberately NOT part of the ordering key.
    # --------------------------------------------------------

    records.sort(
        key=lambda item: (
            _stable_pickle_hash(
                item[0]
            ),
            item[0]
        )
    )

    canonical_units = []

    raw_to_canonical = {}

    for canonical_id, (
        signature,
        raw_id,
        unit
    ) in enumerate(
        records
    ):

        raw_to_canonical[
            int(raw_id)
        ] = canonical_id

        canonical_units.append(
            signature
        )

    return (
        tuple(
            canonical_units
        ),
        raw_to_canonical
    )


# ============================================================
# Object Relations
# ============================================================

def _canonical_object_relation(
    relation,
    unit_map
):
    """
    Canonicalize an object-internal relation.

    Unit IDs are replaced by canonical unit IDs.
    """

    if not isinstance(
        relation,
        dict
    ):

        return _canonicalize_value(
            relation
        )

    source = relation.get(
        "source"
    )

    target = relation.get(
        "target"
    )

    if source is not None:

        source = unit_map.get(
            int(source)
        )

    if target is not None:

        target = unit_map.get(
            int(target)
        )

    result = {}

    for key, value in relation.items():

        if key in (
            "source",
            "target"
        ):

            continue

        result[str(key)] = (
            _canonicalize_value(
                value
            )
        )

    result["source"] = source
    result["target"] = target

    return result


# ============================================================
# Object Signature
# ============================================================

def _object_signature(
    obj,
    unit_map
):
    """
    Structural identity of an object.

    Object ID is intentionally excluded.
    """

    if not isinstance(
        obj,
        dict
    ):

        raise TypeError(
            "object must be a dictionary"
        )

    object_type = obj.get(
        "type"
    )

    # --------------------------------------------------------
    # Parts
    # --------------------------------------------------------

    parts = []

    for raw_unit_id in obj.get(
        "parts",
        []
    ):

        raw_unit_id = int(
            raw_unit_id
        )

        canonical_unit_id = (
            unit_map.get(
                raw_unit_id
            )
        )

        if canonical_unit_id is not None:

            parts.append(
                canonical_unit_id
            )

    # --------------------------------------------------------
    # Unit composition is unordered.
    # --------------------------------------------------------

    parts = tuple(
        sorted(
            parts
        )
    )

    # --------------------------------------------------------
    # Internal relations
    # --------------------------------------------------------

    relations = []

    for relation in obj.get(
        "relations",
        []
    ):

        relations.append(
            _canonical_object_relation(
                relation,
                unit_map
            )
        )

    relations = tuple(
        sorted(
            relations,
            key=_stable_pickle_hash
        )
    )

    # --------------------------------------------------------
    # Additional metadata
    # --------------------------------------------------------

    metadata = {}

    for key, value in obj.items():

        if key in (
            "id",
            "parts",
            "relations"
        ):

            continue

        metadata[str(key)] = (
            _canonicalize_value(
                value
            )
        )

    return (
        "OBJECT",
        WORLD_STATE_VERSION,
        object_type,
        parts,
        relations,
        metadata
    )


# ============================================================
# Object Table
# ============================================================

def _canonical_object_table(
    objects,
    unit_map
):

    records = []

    for raw_id, obj in objects.items():

        signature = _object_signature(
            obj,
            unit_map
        )

        records.append(
            (
                signature,
                int(raw_id)
            )
        )

    records.sort(
        key=lambda item: (
            _stable_pickle_hash(
                item[0]
            ),
            item[0]
        )
    )

    canonical_objects = []

    raw_to_canonical = {}

    for canonical_id, (
        signature,
        raw_id
    ) in enumerate(
        records
    ):

        raw_to_canonical[
            raw_id
        ] = canonical_id

        canonical_objects.append(
            signature
        )

    return (
        tuple(
            canonical_objects
        ),
        raw_to_canonical
    )


# ============================================================
# Instance Signature
# ============================================================

def _instance_signature(
    instance,
    object_map,
    unit_map
):
    """
    Structural identity of one instance.

    Instance ID is intentionally excluded.
    """

    if not isinstance(
        instance,
        dict
    ):

        raise TypeError(
            "instance must be a dictionary"
        )

    # --------------------------------------------------------
    # Object reference
    # --------------------------------------------------------

    object_id = instance.get(
        "object"
    )

    if object_id is not None:

        object_id = object_map.get(
            int(object_id)
        )

    # --------------------------------------------------------
    # Unit parts
    # --------------------------------------------------------

    parts = []

    for raw_unit_id in instance.get(
        "parts",
        []
    ):

        canonical_unit_id = (
            unit_map.get(
                int(raw_unit_id)
            )
        )

        if canonical_unit_id is not None:

            parts.append(
                canonical_unit_id
            )

    parts = tuple(
        sorted(
            parts
        )
    )

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata = {}

    for key, value in instance.items():

        if key in (
            "id",
            "object",
            "parts"
        ):

            continue

        metadata[str(key)] = (
            _canonicalize_value(
                value
            )
        )

    return (
        "INSTANCE",
        WORLD_STATE_VERSION,
        object_id,
        parts,
        metadata
    )


# ============================================================
# Instance Table
# ============================================================

def _canonical_instance_table(
    instances,
    object_map,
    unit_map
):

    records = []

    for raw_id, instance in instances.items():

        signature = _instance_signature(
            instance,
            object_map,
            unit_map
        )

        records.append(
            (
                signature,
                int(raw_id)
            )
        )

    records.sort(
        key=lambda item: (
            _stable_pickle_hash(
                item[0]
            ),
            item[0]
        )
    )

    canonical_instances = []

    for signature, _ in records:

        canonical_instances.append(
            signature
        )

    return tuple(
        canonical_instances
    )


# ============================================================
# World Relation
# ============================================================

def _canonical_world_relation(
    relation,
    object_map
):
    """
    Canonicalize world-level relation.

    Object IDs are replaced by canonical object IDs.
    """

    if not isinstance(
        relation,
        dict
    ):

        return _canonicalize_value(
            relation
        )

    source = relation.get(
        "source"
    )

    target = relation.get(
        "target"
    )

    if source is not None:

        source = object_map.get(
            int(source)
        )

    if target is not None:

        target = object_map.get(
            int(target)
        )

    result = {}

    for key, value in relation.items():

        if key in (
            "source",
            "target"
        ):

            continue

        result[str(key)] = (
            _canonicalize_value(
                value
            )
        )

    result["source"] = source
    result["target"] = target

    return result


# ============================================================
# World Relations
# ============================================================

def _canonical_relations(
    relations,
    object_map
):

    canonical = []

    for relation in relations:

        canonical.append(
            _canonical_world_relation(
                relation,
                object_map
            )
        )

    return tuple(
        sorted(
            canonical,
            key=_stable_pickle_hash
        )
    )


# ============================================================
# WorldState
# ============================================================

class WorldState:

    def __init__(self):

        self.units = {}

        self.objects = {}

        self.instances = {}

        self.relations = []


    # ========================================================
    # Add Unit
    # ========================================================

    def add_unit(
        self,
        unit
    ):

        if not isinstance(
            unit,
            dict
        ):

            raise TypeError(
                "unit must be a dictionary"
            )

        if "id" not in unit:

            raise ValueError(
                "unit requires id"
            )

        unit_id = int(
            unit["id"]
        )

        self.units[
            unit_id
        ] = copy.deepcopy(
            unit
        )


    # ========================================================
    # Add Object
    # ========================================================

    def add_object(
        self,
        obj
    ):

        if not isinstance(
            obj,
            dict
        ):

            raise TypeError(
                "object must be a dictionary"
            )

        if "id" not in obj:

            raise ValueError(
                "object requires id"
            )

        object_id = int(
            obj["id"]
        )

        self.objects[
            object_id
        ] = copy.deepcopy(
            obj
        )


    # ========================================================
    # Add Instance
    # ========================================================

    def add_instance(
        self,
        instance
    ):

        if not isinstance(
            instance,
            dict
        ):

            raise TypeError(
                "instance must be a dictionary"
            )

        if "id" not in instance:

            raise ValueError(
                "instance requires id"
            )

        instance_id = int(
            instance["id"]
        )

        self.instances[
            instance_id
        ] = copy.deepcopy(
            instance
        )


    # ========================================================
    # Add Relation
    # ========================================================

    def add_relation(
        self,
        relation
    ):

        if not isinstance(
            relation,
            dict
        ):

            raise TypeError(
                "relation must be a dictionary"
            )

        self.relations.append(
            copy.deepcopy(
                relation
            )
        )


    # ========================================================
    # Validation
    # ========================================================

    def validate(self):

        errors = []

        # ----------------------------------------------------
        # Unit references
        # ----------------------------------------------------

        known_units = set(
            self.units.keys()
        )

        for object_id, obj in self.objects.items():

            for unit_id in obj.get(
                "parts",
                []
            ):

                if int(unit_id) not in known_units:

                    errors.append(
                        "Object {} references missing unit {}".format(
                            object_id,
                            unit_id
                        )
                    )

            for relation in obj.get(
                "relations",
                []
            ):

                if "source" in relation:

                    if int(
                        relation["source"]
                    ) not in known_units:

                        errors.append(
                            "Object {} relation references "
                            "missing source unit {}".format(
                                object_id,
                                relation["source"]
                            )
                        )

                if "target" in relation:

                    if int(
                        relation["target"]
                    ) not in known_units:

                        errors.append(
                            "Object {} relation references "
                            "missing target unit {}".format(
                                object_id,
                                relation["target"]
                            )
                        )

        # ----------------------------------------------------
        # Object references
        # ----------------------------------------------------

        known_objects = set(
            self.objects.keys()
        )

        for instance_id, instance in self.instances.items():

            if "object" in instance:

                object_id = int(
                    instance["object"]
                )

                if object_id not in known_objects:

                    errors.append(
                        "Instance {} references missing object {}".format(
                            instance_id,
                            object_id
                        )
                    )

        # ----------------------------------------------------
        # World relations
        # ----------------------------------------------------

        for index, relation in enumerate(
            self.relations
        ):

            if "source" in relation:

                if int(
                    relation["source"]
                ) not in known_objects:

                    errors.append(
                        "Relation {} references missing "
                        "source object {}".format(
                            index,
                            relation["source"]
                        )
                    )

            if "target" in relation:

                if int(
                    relation["target"]
                ) not in known_objects:

                    errors.append(
                        "Relation {} references missing "
                        "target object {}".format(
                            index,
                            relation["target"]
                        )
                    )

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }


    # ========================================================
    # Canonical Statistics
    # ========================================================

    def canonical_statistics(self):

        return {
            "units": len(
                self.units
            ),
            "objects": len(
                self.objects
            ),
            "instances": len(
                self.instances
            ),
            "relations": len(
                self.relations
            )
        }


    # ========================================================
    # Canonical Payload
    # ========================================================

    def canonical_payload(self):

        # ----------------------------------------------------
        # 1. Canonicalize units.
        #
        # Raw unit IDs disappear here.
        # ----------------------------------------------------

        (
            canonical_units,
            unit_map
        ) = _canonical_unit_table(
            self.units
        )

        # ----------------------------------------------------
        # 2. Canonicalize objects.
        #
        # Object parts now reference canonical unit IDs.
        # ----------------------------------------------------

        (
            canonical_objects,
            object_map
        ) = _canonical_object_table(
            self.objects,
            unit_map
        )

        # ----------------------------------------------------
        # 3. Canonicalize instances.
        # ----------------------------------------------------

        canonical_instances = (
            _canonical_instance_table(
                self.instances,
                object_map,
                unit_map
            )
        )

        # ----------------------------------------------------
        # 4. Canonicalize world relations.
        # ----------------------------------------------------

        canonical_relations = (
            _canonical_relations(
                self.relations,
                object_map
            )
        )

        # ----------------------------------------------------
        # Final immutable payload.
        #
        # No raw IDs appear anywhere in the structural
        # representation.
        # ----------------------------------------------------

        return {
            "version": WORLD_STATE_VERSION,

            "statistics": self.canonical_statistics(),

            "units": canonical_units,

            "objects": canonical_objects,

            "instances": canonical_instances,

            "relations": canonical_relations
        }


    # ========================================================
    # Canonical Signature
    # ========================================================

    def canonical_signature(self):

        return self.canonical_payload()


    # ========================================================
    # Canonical Hash
    # ========================================================

    def canonical_hash(self):

        payload = self.canonical_payload()

        data = pickle.dumps(
            payload,
            protocol=4
        )

        return hashlib.sha256(
            data
        ).hexdigest()


# ============================================================
# End
# ============================================================