# ============================================================
# Struct3D v2.6
# structure/unit_relation.py
#
# Structural Unit Relation Graph
#
# Converts:
#
#     point-level structural evidence
#
# into:
#
#     unit-level structural relations
#
# CPU only
# ============================================================

import numpy as np


class StructuralUnitRelationGraph:

    def __init__(
        self,
        near_threshold=1.5,
        contact_threshold=0.2
    ):

        self.near_threshold = float(
            near_threshold
        )

        self.contact_threshold = float(
            contact_threshold
        )

    # ========================================================
    # Unit center
    # ========================================================

    def center(
        self,
        unit
    ):

        points = np.asarray(
            unit.points,
            dtype=float
        )

        if len(points) == 0:

            return np.zeros(3)

        return np.mean(
            points,
            axis=0
        )

    # ========================================================
    # Unit radius
    # ========================================================

    def radius(
        self,
        unit
    ):

        points = np.asarray(
            unit.points,
            dtype=float
        )

        if len(points) == 0:

            return 0.0

        c = self.center(
            unit
        )

        return float(
            np.max(
                np.linalg.norm(
                    points - c,
                    axis=1
                )
            )
        )

    # ========================================================
    # Pair relation
    # ========================================================

    def pair_relation(
        self,
        unit_a,
        unit_b
    ):

        ca = self.center(
            unit_a
        )

        cb = self.center(
            unit_b
        )

        center_distance = float(
            np.linalg.norm(
                ca - cb
            )
        )

        ra = self.radius(
            unit_a
        )

        rb = self.radius(
            unit_b
        )

        # Approximate surface gap

        gap = max(
            0.0,
            center_distance - ra - rb
        )

        if gap <= self.contact_threshold:

            relation_type = (
                "touching"
            )

        elif gap <= self.near_threshold:

            relation_type = (
                "near"
            )

        else:

            relation_type = (
                "separate"
            )

        return {

            "units": [
                int(unit_a._struct_id),
                int(unit_b._struct_id)
            ],

            "type":
                relation_type,

            "distance":
                center_distance,

            "gap":
                gap
        }

    # ========================================================
    # Build
    # ========================================================

    def build(
        self,
        units
    ):

        # deterministic IDs

        for i, unit in enumerate(
            units
        ):

            unit._struct_id = int(i)

        relations = []

        n = len(
            units
        )

        for i in range(n):

            for j in range(
                i + 1,
                n
            ):

                relation = (
                    self.pair_relation(
                        units[i],
                        units[j]
                    )
                )

                relations.append(
                    relation
                )

        return relations