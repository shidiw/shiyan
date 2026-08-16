# ============================================================
# Struct3D v2.9
# structure/assembly.py
#
# Typed Structural Object Assembly
#
# Core principle:
#
#   Structural Object
#       =
#   Connected Component of Assembly Relations
#
# Structural Relations are NOT automatically used for
# object fusion.
#
# Relation hierarchy:
#
#   Unit
#     |
#     +-- Assembly Relation
#     |       |
#     |       +--> Object formation
#     |
#     +-- Structural Relation
#             |
#             +--> Object-level relation projection
#
# CPU only
# ============================================================

import numpy as np


# ============================================================
# Structural Object
# ============================================================

class StructuralObject:

    def __init__(
        self,
        parts=None,
        relations=None,
        object_id=None,
        object_type="single"
    ):

        self.id = object_id

        self.parts = (
            parts
            if parts is not None
            else []
        )

        self.relations = (
            relations
            if relations is not None
            else []
        )

        self.type = object_type

        self.center = np.zeros(3)

        self.energy = 0.0

        self.primitives = []

        self.parameters = []

        self.num_parts = 0

        self.num_points = 0

        self.primitive = None

        self.update()

    # --------------------------------------------------------
    # Generic value access
    # --------------------------------------------------------

    def get_value(
        self,
        obj,
        key,
        default=None
    ):

        if isinstance(
            obj,
            dict
        ):

            return obj.get(
                key,
                default
            )

        return getattr(
            obj,
            key,
            default
        )

    # --------------------------------------------------------
    # Update
    # --------------------------------------------------------

    def update(self):

        self.num_parts = len(
            self.parts
        )

        centers = []

        self.primitives = []

        self.parameters = []

        self.energy = 0.0

        self.num_points = 0

        # ----------------------------------------------------
        # Collect structural unit information
        # ----------------------------------------------------

        for part in self.parts:

            # ------------------------------------------------
            # Center
            # ------------------------------------------------

            c = self.get_value(
                part,
                "center",
                np.zeros(3)
            )

            if callable(c):

                c = c()

            try:

                c = np.asarray(
                    c,
                    dtype=float
                ).reshape(-1)

                if c.size >= 3:

                    centers.append(
                        c[:3]
                    )

            except Exception:

                pass

            # ------------------------------------------------
            # Primitive
            # ------------------------------------------------

            primitive = self.get_value(
                part,
                "primitive",
                "unknown"
            )

            self.primitives.append(
                primitive
            )

            # ------------------------------------------------
            # Parameters
            # ------------------------------------------------

            para = self.get_value(
                part,
                "parameters",
                {}
            )

            if para is None:

                para = {}

            elif isinstance(
                para,
                dict
            ):

                para = dict(
                    para
                )

            elif isinstance(
                para,
                (list, tuple)
            ):

                merged = {}

                for item in para:

                    if isinstance(
                        item,
                        dict
                    ):

                        merged.update(
                            item
                        )

                para = merged

            else:

                para = {}

            self.parameters.append(
                para
            )

            # ------------------------------------------------
            # Energy
            # ------------------------------------------------

            e = self.get_value(
                part,
                "energy",
                0.0
            )

            if isinstance(
                e,
                dict
            ):

                e = e.get(
                    "value",
                    0.0
                )

            try:

                self.energy += float(
                    e
                )

            except Exception:

                pass

            # ------------------------------------------------
            # Point count
            # ------------------------------------------------

            pts = self.get_value(
                part,
                "points",
                []
            )

            try:

                self.num_points += len(
                    pts
                )

            except Exception:

                pass

        # ----------------------------------------------------
        # Object center
        # ----------------------------------------------------

        if len(centers) > 0:

            self.center = np.mean(
                np.asarray(
                    centers
                ),
                axis=0
            )

        else:

            self.center = np.zeros(
                3,
                dtype=float
            )

        # ----------------------------------------------------
        # Mean structural energy
        # ----------------------------------------------------

        if self.num_parts > 0:

            self.energy /= (
                self.num_parts
            )

        # ----------------------------------------------------
        # Compatibility primitive
        # ----------------------------------------------------

        if len(
            self.primitives
        ) > 0:

            self.primitive = (
                self.primitives[0]
            )

        else:

            self.primitive = None

    # --------------------------------------------------------
    # Info
    # --------------------------------------------------------

    def info(self):

        return {

            "id":
                self.id,

            "type":
                self.type,

            "parts":
                self.num_parts,

            "points":
                self.num_points,

            "center":
                self.center,

            "energy":
                self.energy,

            "primitive":
                self.primitive,

            "primitives":
                self.primitives,

            "parameters":
                self.parameters,

            "relations":
                self.relations
        }


# ============================================================
# Disjoint Set Union
# ============================================================

class DisjointSet:

    def __init__(
        self,
        n
    ):

        self.parent = list(
            range(n)
        )

        self.rank = [
            0
            for _ in range(n)
        ]

    # --------------------------------------------------------
    # Find
    # --------------------------------------------------------

    def find(
        self,
        x
    ):

        if self.parent[x] != x:

            self.parent[x] = self.find(
                self.parent[x]
            )

        return self.parent[x]

    # --------------------------------------------------------
    # Union
    # --------------------------------------------------------

    def union(
        self,
        a,
        b
    ):

        ra = self.find(
            a
        )

        rb = self.find(
            b
        )

        if ra == rb:

            return

        if self.rank[ra] < self.rank[rb]:

            self.parent[ra] = rb

        elif self.rank[ra] > self.rank[rb]:

            self.parent[rb] = ra

        else:

            self.parent[rb] = ra

            self.rank[ra] += 1


# ============================================================
# Structural Object Assembly
# ============================================================

class StructuralObjectAssembly:

    """
    Typed structural relation assembly.

    ----------------------------------------------------------
    Core definition
    ----------------------------------------------------------

        Object
        =
        Connected Component(
            Unit Graph,
            Assembly Relations
        )

    ----------------------------------------------------------
    Relation semantics
    ----------------------------------------------------------

    Assembly Relations:

        same
        same_object
        part_of
        component_of
        rigidly_connected

    These relations are allowed to fuse units into the same
    structural object.

    Structural Relations:

        connected
        contact
        touching
        adjacent
        symmetry
        near
        support
        attached

    These relations describe interactions between structural
    entities and DO NOT automatically fuse them into one object.

    ----------------------------------------------------------
    Projection
    ----------------------------------------------------------

        Unit Relation
            |
            v
        Object Relation
            |
            v
        Instance Relation
    """

    # ========================================================
    # Assembly Relations
    # ========================================================

    ASSEMBLY_RELATION_TYPES = {

        "same",

        "same_object",

        "part_of",

        "component_of",

        "rigidly_connected"
    }

    # ========================================================
    # Structural Relations
    # ========================================================

    STRUCTURAL_RELATION_TYPES = {

        "connected",

        "contact",

        "touching",

        "adjacent",

        "symmetry",

        "near",

        "support",

        "attached"
    }

    # ========================================================
    # Constructor
    # ========================================================

    def __init__(
        self,
        threshold=0.6
    ):

        self.threshold = float(
            threshold
        )

        self.objects = []

        self.assembly_relations = []

        self.structural_relations = []

    # ========================================================
    # Relation Type
    # ========================================================

    def relation_type(
        self,
        relation
    ):

        if not isinstance(
            relation,
            dict
        ):

            return ""

        return str(
            relation.get(
                "type",
                relation.get(
                    "relation",
                    ""
                )
            )
        )

    # ========================================================
    # Assembly Relation
    # ========================================================

    def is_assembly_relation(
        self,
        relation
    ):

        relation_type = self.relation_type(
            relation
        )

        return (
            relation_type
            in
            self.ASSEMBLY_RELATION_TYPES
        )

    # ========================================================
    # Structural Relation
    # ========================================================

    def is_structural_relation(
        self,
        relation
    ):

        relation_type = self.relation_type(
            relation
        )

        return (
            relation_type
            in
            self.STRUCTURAL_RELATION_TYPES
        )

    # ========================================================
    # Generic Compatible
    # ========================================================

    def compatible(
        self,
        relation
    ):

        return self.is_assembly_relation(
            relation
        )

    # ========================================================
    # Extract Relation Endpoints
    # ========================================================

    def relation_ids(
        self,
        relation
    ):

        if not isinstance(
            relation,
            dict
        ):

            return None

        # ----------------------------------------------------
        # Explicit unit endpoint list
        # ----------------------------------------------------

        ids = relation.get(
            "units"
        )

        if ids is None:

            ids = relation.get(
                "objects"
            )

        # ----------------------------------------------------
        # source / target
        # ----------------------------------------------------

        if ids is None:

            source = relation.get(
                "source"
            )

            target = relation.get(
                "target"
            )

            if (
                source is not None
                and
                target is not None
            ):

                ids = [
                    source,
                    target
                ]

        if ids is None:

            return None

        try:

            if len(ids) != 2:

                return None

        except Exception:

            return None

        try:

            a = int(
                ids[0]
            )

            b = int(
                ids[1]
            )

        except Exception:

            return None

        return a, b

    # ========================================================
    # Relation Confidence
    # ========================================================

    def relation_confidence(
        self,
        relation
    ):

        if not isinstance(
            relation,
            dict
        ):

            return 0.0

        value = relation.get(
            "confidence",
            1.0
        )

        try:

            return float(
                value
            )

        except Exception:

            return 0.0

    # ========================================================
    # Unit -> Object Mapping
    # ========================================================

    def build_unit_object_map(
        self,
        units,
        objects
    ):
        """
        Canonical mapping:

            unit_index -> object_id

        Structural unit identity is determined by its position
        inside the canonical units list.

        We intentionally do NOT rely on StructuralUnit.id.
        """

        unit_to_object = {}

        # ----------------------------------------------------
        # Object -> contained units
        # ----------------------------------------------------

        for object_id, obj in enumerate(
            objects
        ):

            for part in obj.parts:

                # ------------------------------------------------
                # Identity-based matching
                # ------------------------------------------------

                for unit_id, unit in enumerate(
                    units
                ):

                    if part is unit:

                        unit_to_object[
                            unit_id
                        ] = object_id

                        break

        return unit_to_object

    # ========================================================
    # Project Unit Relations -> Object Relations
    # ========================================================

    def project_relations(
        self,
        units,
        objects,
        relations
    ):
        """
        Project structural unit relations to object relations.

        Important:

        Assembly relations are NOT projected as external object
        relations because they define object membership.

        Structural relations ARE projected.

        Example:

            U0 -- same_object -- U1
            U1 -- connected   -- U2

        becomes:

            O0 -- connected -- O1

        while the same_object relation is absorbed into O0.
        """

        unit_to_object = (
            self.build_unit_object_map(
                units,
                objects
            )
        )

        projected = []

        seen = set()

        for relation in relations:

            if not isinstance(
                relation,
                dict
            ):

                continue

            # ------------------------------------------------
            # Only structural relations are projected.
            # ------------------------------------------------

            if self.is_assembly_relation(
                relation
            ):

                continue

            # ------------------------------------------------
            # Endpoint extraction
            # ------------------------------------------------

            ids = self.relation_ids(
                relation
            )

            if ids is None:

                continue

            a, b = ids

            # ------------------------------------------------
            # Unit existence
            # ------------------------------------------------

            if (
                a not in unit_to_object
                or
                b not in unit_to_object
            ):

                continue

            object_a = unit_to_object[
                a
            ]

            object_b = unit_to_object[
                b
            ]

            # ------------------------------------------------
            # Internal relation
            # ------------------------------------------------

            if object_a == object_b:

                continue

            # ------------------------------------------------
            # Canonical unordered pair
            # ------------------------------------------------

            pair = tuple(
                sorted(
                    [
                        object_a,
                        object_b
                    ]
                )
            )

            relation_type = (
                self.relation_type(
                    relation
                )
            )

            key = (
                pair[0],
                pair[1],
                relation_type
            )

            if key in seen:

                continue

            seen.add(
                key
            )

            # ------------------------------------------------
            # Preserve metadata
            # ------------------------------------------------

            record = dict(
                relation
            )

            # Remove unit-level endpoint forms.
            record.pop(
                "units",
                None
            )

            record.pop(
                "objects",
                None
            )

            # ------------------------------------------------
            # Object-level endpoints
            # ------------------------------------------------

            record["source"] = (
                pair[0]
            )

            record["target"] = (
                pair[1]
            )

            record["type"] = (
                relation_type
            )

            # ------------------------------------------------
            # Traceability
            # ------------------------------------------------

            record["unit_source"] = (
                a
            )

            record["unit_target"] = (
                b
            )

            projected.append(
                record
            )

        # ----------------------------------------------------
        # Deterministic ordering
        # ----------------------------------------------------

        projected.sort(
            key=lambda r: (
                int(
                    r.get(
                        "source",
                        -1
                    )
                ),
                int(
                    r.get(
                        "target",
                        -1
                    )
                ),
                str(
                    r.get(
                        "type",
                        "unknown"
                    )
                )
            )
        )

        return projected

    # ========================================================
    # Build
    # ========================================================

    def build(
        self,
        units,
        relations
    ):
        """
        Build structural objects.

        Only Assembly Relations can merge units.

        Structural Relations are retained separately and later
        projected through project_relations().
        """

        self.objects = []

        self.assembly_relations = []

        self.structural_relations = []

        n = len(
            units
        )

        if n == 0:

            return []

        # ----------------------------------------------------
        # Disjoint Set Union
        # ----------------------------------------------------

        dsu = DisjointSet(
            n
        )

        # ----------------------------------------------------
        # Classify relations
        # ----------------------------------------------------

        for relation in relations:

            if not isinstance(
                relation,
                dict
            ):

                continue

            relation_type = (
                self.relation_type(
                    relation
                )
            )

            # =================================================
            # Assembly Relation
            # =================================================

            if (
                relation_type
                in
                self.ASSEMBLY_RELATION_TYPES
            ):

                confidence = (
                    self.relation_confidence(
                        relation
                    )
                )

                # ------------------------------------------------
                # Threshold
                # ------------------------------------------------

                if confidence < self.threshold:

                    continue

                ids = self.relation_ids(
                    relation
                )

                if ids is None:

                    continue

                a, b = ids

                if (
                    a < 0
                    or
                    b < 0
                    or
                    a >= n
                    or
                    b >= n
                ):

                    continue

                if a == b:

                    continue

                # ------------------------------------------------
                # Fuse
                # ------------------------------------------------

                dsu.union(
                    a,
                    b
                )

                self.assembly_relations.append(
                    relation
                )

            # =================================================
            # Structural Relation
            # =================================================

            elif (
                relation_type
                in
                self.STRUCTURAL_RELATION_TYPES
            ):

                self.structural_relations.append(
                    relation
                )

            # =================================================
            # Unknown Relation
            # =================================================

            else:

                # Unknown relations are preserved as structural
                # metadata but do not participate in assembly.
                self.structural_relations.append(
                    relation
                )

        # ----------------------------------------------------
        # Connected Components
        # ----------------------------------------------------

        components = {}

        for i in range(
            n
        ):

            root = dsu.find(
                i
            )

            if root not in components:

                components[root] = []

            components[root].append(
                i
            )

        # ----------------------------------------------------
        # Deterministic component ordering
        # ----------------------------------------------------

        component_list = sorted(
            components.values(),
            key=lambda x: min(x)
        )

        # ----------------------------------------------------
        # Construct Objects
        # ----------------------------------------------------

        for object_id, unit_ids in enumerate(
            component_list
        ):

            parts = [
                units[i]
                for i in unit_ids
            ]

            # ------------------------------------------------
            # Relations internal to this object
            #
            # Only assembly relations are stored here.
            # External structural relations are projected later.
            # ------------------------------------------------

            object_relations = []

            unit_set = set(
                unit_ids
            )

            for relation in (
                self.assembly_relations
            ):

                ids = self.relation_ids(
                    relation
                )

                if ids is None:

                    continue

                a, b = ids

                if (
                    a in unit_set
                    and
                    b in unit_set
                ):

                    object_relations.append(
                        relation
                    )

            # ------------------------------------------------
            # Object type
            # ------------------------------------------------

            if len(unit_ids) == 1:

                object_type = (
                    "single"
                )

            else:

                object_type = (
                    "assembly"
                )

            # ------------------------------------------------
            # Create object
            # ------------------------------------------------

            obj = StructuralObject(

                parts=parts,

                relations=object_relations,

                object_id=object_id,

                object_type=object_type
            )

            self.objects.append(
                obj
            )

        return self.objects

    # ========================================================
    # Show
    # ========================================================

    def show(
        self,
        objects=None
    ):

        if objects is None:

            objects = self.objects

        print(
            "\nStructural Object Assembly"
        )

        for obj in objects:

            print(
                "\nObject",
                obj.id
            )

            print(
                obj.info()
            )

    # ========================================================
    # Statistics
    # ========================================================

    def statistics(
        self,
        objects=None
    ):

        if objects is None:

            objects = self.objects

        print(
            "\nAssembly Statistics"
        )

        print(
            "Objects:",
            len(objects)
        )

        print(
            "Assembly relations:",
            len(
                self.assembly_relations
            )
        )

        print(
            "Structural relations:",
            len(
                self.structural_relations
            )
        )

        for obj in objects:

            print(
                "Object",
                obj.id,
                "parts:",
                obj.num_parts,
                "type:",
                obj.type
            )


# ============================================================
# Compatibility Aliases
# ============================================================

StructuralAssembly = (
    StructuralObjectAssembly
)

ObjectAssembly = (
    StructuralObjectAssembly
)


# ============================================================
# Public API
# ============================================================

__all__ = [

    "StructuralObject",

    "DisjointSet",

    "StructuralObjectAssembly",

    "StructuralAssembly",

    "ObjectAssembly"

]