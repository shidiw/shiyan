# ============================================================
# Struct3D v2.6
# structure/assembly.py
#
# Structural Object Assembly
#
# CPU only
#
# Principle:
#
#   Structural Units
#          ↓
#   Structural Relations
#          ↓
#   Relation Graph
#          ↓
#   Connected Components
#          ↓
#   Structural Objects
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
            list(parts)
            if parts is not None
            else []
        )

        self.relations = (
            list(relations)
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

    # ========================================================
    # Generic getter
    # ========================================================

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

    # ========================================================
    # Update
    # ========================================================

    def update(self):

        self.num_parts = len(
            self.parts
        )

        self.center = np.zeros(3)

        self.energy = 0.0

        self.primitives = []

        self.parameters = []

        self.num_points = 0

        centers = []

        # ----------------------------------------------------
        # Collect structural information
        # ----------------------------------------------------

        for part in self.parts:

            # center

            center = self.get_value(
                part,
                "center",
                None
            )

            if callable(center):

                center = center()

            if center is not None:

                try:

                    center = np.asarray(
                        center,
                        dtype=float
                    ).reshape(-1)

                    if center.size >= 3:

                        centers.append(
                            center[:3]
                        )

                except Exception:

                    pass

            # primitive

            primitive = self.get_value(
                part,
                "primitive",
                "unknown"
            )

            self.primitives.append(
                primitive
            )

            # parameters

            parameters = self.get_value(
                part,
                "parameters",
                {}
            )

            if parameters is None:

                parameters = {}

            elif isinstance(
                parameters,
                dict
            ):

                parameters = dict(
                    parameters
                )

            elif isinstance(
                parameters,
                (list, tuple)
            ):

                merged = {}

                for item in parameters:

                    if isinstance(
                        item,
                        dict
                    ):

                        merged.update(
                            item
                        )

                parameters = merged

            else:

                parameters = {}

            self.parameters.append(
                parameters
            )

            # energy

            energy = self.get_value(
                part,
                "energy",
                0.0
            )

            try:

                if isinstance(
                    energy,
                    dict
                ):

                    energy = energy.get(
                        "value",
                        0.0
                    )

                self.energy += float(
                    energy
                )

            except Exception:

                pass

            # points

            points = self.get_value(
                part,
                "points",
                []
            )

            try:

                self.num_points += len(
                    points
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

        if len(self.primitives) > 0:

            self.primitive = (
                self.primitives[0]
            )

    # ========================================================
    # Info
    # ========================================================

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
                len(self.relations)
        }


# ============================================================
# Structural Object Assembly
# ============================================================

class StructuralObjectAssembly:

    """
    Assemble structural units according to relations.

    v2.6 principle:

        Object = connected component of
                 compatible structural relation graph.

    This removes the old greedy pairwise limitation.
    """

    def __init__(
        self,
        threshold=0.6
    ):

        self.threshold = float(
            threshold
        )

        self.objects = []

    # ========================================================
    # Relation utilities
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

        return relation.get(
            "type",
            relation.get(
                "relation",
                ""
            )
        )

    def relation_weight(
        self,
        relation
    ):

        if not isinstance(
            relation,
            dict
        ):

            return 0.0

        try:

            return float(
                relation.get(
                    "weight",
                    relation.get(
                        "affinity",
                        0.0
                    )
                )
            )

        except Exception:

            return 0.0

    def relation_units(
        self,
        relation
    ):

        if not isinstance(
            relation,
            dict
        ):

            return None

        ids = relation.get(
            "units",
            relation.get(
                "objects",
                None
            )
        )

        if ids is None:

            return None

        if len(ids) != 2:

            return None

        return (
            int(ids[0]),
            int(ids[1])
        )

    # ========================================================
    # Compatibility
    # ========================================================

    def compatible(
        self,
        relation
    ):

        if not isinstance(
            relation,
            dict
        ):

            return False

        relation_type = (
            self.relation_type(
                relation
            )
        )

        # Explicit structural relations

        if relation_type in [

            "connected",

            "contact",

            "touching",

            "adjacent",

            "symmetry",

            "same",

            "same_object"

        ]:

            return True

        # Weighted graph relation

        weight = self.relation_weight(
            relation
        )

        if (
            relation_type
            in [
                "affinity",
                "near",
                "graph"
            ]
            and
            weight >= self.threshold
        ):

            return True

        return False

    # ========================================================
    # Union-Find
    # ========================================================

    def _find(
        self,
        parent,
        x
    ):

        while parent[x] != x:

            parent[x] = parent[
                parent[x]
            ]

            x = parent[x]

        return x

    def _union(
        self,
        parent,
        rank,
        a,
        b
    ):

        ra = self._find(
            parent,
            a
        )

        rb = self._find(
            parent,
            b
        )

        if ra == rb:

            return

        if rank[ra] < rank[rb]:

            parent[ra] = rb

        elif rank[ra] > rank[rb]:

            parent[rb] = ra

        else:

            parent[rb] = ra

            rank[ra] += 1

    # ========================================================
    # Build
    # ========================================================

    def build(
        self,
        units,
        relations
    ):

        self.objects = []

        n = len(
            units
        )

        if n == 0:

            return []

        # ----------------------------------------------------
        # Union-Find initialization
        # ----------------------------------------------------

        parent = list(
            range(n)
        )

        rank = [0] * n

        # ----------------------------------------------------
        # Compatible structural relations
        # ----------------------------------------------------

        relation_groups = {}

        for relation in relations:

            if not self.compatible(
                relation
            ):

                continue

            ids = self.relation_units(
                relation
            )

            if ids is None:

                continue

            a, b = ids

            if (
                a < 0
                or
                a >= n
                or
                b < 0
                or
                b >= n
            ):

                continue

            self._union(
                parent,
                rank,
                a,
                b
            )

        # ----------------------------------------------------
        # Group units by component
        # ----------------------------------------------------

        components = {}

        for i in range(n):

            root = self._find(
                parent,
                i
            )

            if root not in components:

                components[root] = []

            components[root].append(
                i
            )

        # ----------------------------------------------------
        # Deterministic ordering
        # ----------------------------------------------------

        groups = sorted(
            components.values(),
            key=lambda x: (
                min(x)
            )
        )

        # ----------------------------------------------------
        # Build Structural Objects
        # ----------------------------------------------------

        oid = 0

        for group in groups:

            group_set = set(
                group
            )

            object_relations = []

            for relation in relations:

                ids = self.relation_units(
                    relation
                )

                if ids is None:

                    continue

                a, b = ids

                if (
                    a in group_set
                    and
                    b in group_set
                ):

                    object_relations.append(
                        relation
                    )

            parts = [
                units[i]
                for i in group
            ]

            if len(parts) > 1:

                object_type = (
                    "assembly"
                )

            else:

                object_type = (
                    "single"
                )

            obj = StructuralObject(

                parts=parts,

                relations=object_relations,

                object_id=oid,

                object_type=object_type
            )

            self.objects.append(
                obj
            )

            oid += 1

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

            print()

            print(
                "Object",
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

        for obj in objects:

            print(
                "Object",
                obj.id,
                "parts:",
                obj.num_parts,
                "relations:",
                len(obj.relations)
            )


# ============================================================
# Compatibility aliases
# ============================================================

StructuralAssembly = (
    StructuralObjectAssembly
)

ObjectAssembly = (
    StructuralObjectAssembly
)


__all__ = [

    "StructuralObject",

    "StructuralObjectAssembly",

    "StructuralAssembly",

    "ObjectAssembly"

]