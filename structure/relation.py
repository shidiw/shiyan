# ============================================================
# Struct3D v2.6
# structure/relation.py
#
# Structural Relation Graph
#
# G = (V, E, W)
#
# Invariance:
#   translation
#   rotation
#   reflection of normal orientation
#   permutation of point ordering
#
# CPU only
# ============================================================

import numpy as np


class StructuralGraph:

    """
    Struct3D Structural Relation Graph

    G = (V, E, W)

    E:
        directed KNN edges

    W:
        structural affinity

    The affinity is invariant to:

        1. translation
        2. rotation
        3. normal sign flip
        4. point permutation
    """

    def __init__(
        self,
        k=15,
        sigma_x=None,
        sigma_n=0.5,
        sigma_k=0.05,
        alpha=1.0,
        beta=1.0
    ):

        self.k = int(k)

        self.sigma_x = sigma_x

        self.sigma_n = float(sigma_n)

        self.sigma_k = float(sigma_k)

        self.alpha = float(alpha)

        self.beta = float(beta)

    # ========================================================
    # Characteristic spatial scale
    # ========================================================

    def estimate_sigma_x(
        self,
        points
    ):

        N = len(points)

        if N <= 1:
            return 1.0

        kk = min(
            self.k,
            N - 1
        )

        distances = []

        for i in range(N):

            d = np.linalg.norm(
                points - points[i],
                axis=1
            )

            d.sort()

            local = d[1:kk + 1]

            if len(local) > 0:

                distances.extend(
                    local.tolist()
                )

        if len(distances) == 0:
            return 1.0

        sigma = float(
            np.median(
                np.asarray(
                    distances,
                    dtype=float
                )
            )
        )

        return max(
            sigma,
            1e-12
        )

    # ========================================================
    # Build point graph
    # ========================================================

    def build(
        self,
        points,
        normals,
        curvature
    ):

        points = np.asarray(
            points,
            dtype=float
        )

        normals = np.asarray(
            normals,
            dtype=float
        )

        curvature = np.asarray(
            curvature,
            dtype=float
        )

        N = len(points)

        if N == 0:

            return {
                "edges": np.empty(
                    (0, 2),
                    dtype=np.int32
                ),

                "weights": np.empty(
                    (0,),
                    dtype=np.float32
                )
            }

        # ----------------------------------------------------
        # Normalize normals
        # ----------------------------------------------------

        normal_norm = np.linalg.norm(
            normals,
            axis=1,
            keepdims=True
        )

        normals = normals / np.maximum(
            normal_norm,
            1e-12
        )

        # ----------------------------------------------------
        # Permutation invariant scale
        # ----------------------------------------------------

        if self.sigma_x is None:

            sigma_x = self.estimate_sigma_x(
                points
            )

        else:

            sigma_x = float(
                self.sigma_x
            )

        self.sigma_x = max(
            sigma_x,
            1e-12
        )

        edges = []

        weights = []

        # ====================================================
        # KNN
        # ====================================================

        for i in range(N):

            dist = np.linalg.norm(
                points - points[i],
                axis=1
            )

            neighbors = np.argsort(
                dist,
                kind="mergesort"
            )[1:self.k + 1]

            for j in neighbors:

                w = self.edge_weight(
                    points[i],
                    points[j],
                    normals[i],
                    normals[j],
                    curvature[i],
                    curvature[j]
                )

                edges.append(
                    [
                        i,
                        int(j)
                    ]
                )

                weights.append(
                    w
                )

        return {
            "edges": np.asarray(
                edges,
                dtype=np.int32
            ),

            "weights": np.asarray(
                weights,
                dtype=np.float32
            )
        }

    # ========================================================
    # Normal distance
    # ========================================================

    def normal_distance(
        self,
        ni,
        nj
    ):

        ni = np.asarray(
            ni,
            dtype=float
        )

        nj = np.asarray(
            nj,
            dtype=float
        )

        ni_norm = np.linalg.norm(
            ni
        )

        nj_norm = np.linalg.norm(
            nj
        )

        if (
            ni_norm < 1e-12
            or
            nj_norm < 1e-12
        ):

            return 1.0

        ni = ni / ni_norm

        nj = nj / nj_norm

        cosine = abs(
            float(
                np.dot(
                    ni,
                    nj
                )
            )
        )

        cosine = np.clip(
            cosine,
            0.0,
            1.0
        )

        return 1.0 - cosine

    # ========================================================
    # Edge weight
    # ========================================================

    def edge_weight(
        self,
        xi,
        xj,
        ni,
        nj,
        ki,
        kj
    ):

        dx = np.linalg.norm(
            xi - xj
        )

        spatial_energy = (
            dx * dx
            /
            (
                self.sigma_x ** 2
                +
                1e-12
            )
        )

        dn = self.normal_distance(
            ni,
            nj
        )

        normal_energy = (
            self.alpha
            *
            dn * dn
            /
            (
                self.sigma_n ** 2
                +
                1e-12
            )
        )

        dk = abs(
            float(ki) - float(kj)
        )

        curvature_energy = (
            self.beta
            *
            dk * dk
            /
            (
                self.sigma_k ** 2
                +
                1e-12
            )
        )

        energy = (
            spatial_energy
            +
            normal_energy
            +
            curvature_energy
        )

        return float(
            np.exp(
                -energy
            )
        )

    # ========================================================
    # Convert graph to relation records
    # ========================================================

    def to_relations(
        self,
        graph,
        threshold=0.6
    ):

        """
        Convert graph representation:

            edges + weights

        into canonical structural relations.

        Output:

        [
            {
                "units": [i, j],
                "type": "...",
                "weight": ...
            }
        ]
        """

        edges = graph.get(
            "edges",
            np.empty(
                (0, 2),
                dtype=np.int32
            )
        )

        weights = graph.get(
            "weights",
            np.empty(
                (0,),
                dtype=np.float32
            )
        )

        relations = []

        for idx, edge in enumerate(edges):

            i = int(edge[0])

            j = int(edge[1])

            w = float(
                weights[idx]
            )

            if w >= threshold:

                relation_type = "connected"

            elif w >= threshold * 0.5:

                relation_type = "adjacent"

            else:

                relation_type = "separate"

            relations.append(
                {
                    "units": [
                        i,
                        j
                    ],

                    "type":
                        relation_type,

                    "weight":
                        w
                }
            )

        return relations

    # ========================================================
    # Statistics
    # ========================================================

    def statistics(
        self,
        graph
    ):

        edges = graph["edges"]

        weights = graph["weights"]

        print(
            "\nStructural Graph"
        )

        print(
            "Nodes:",
            len(
                np.unique(
                    edges
                )
            )
        )

        print(
            "Edges:",
            len(edges)
        )

        if len(weights) == 0:
            return

        print(
            "Weight mean:",
            np.mean(weights)
        )

        print(
            "Weight std:",
            np.std(weights)
        )

        print(
            "Weight min:",
            np.min(weights)
        )

        print(
            "Weight max:",
            np.max(weights)
        )

# ============================================================
# Struct3D Structural Relation Graph
#
# Unit-level structural relations
#
# This layer is intentionally separated from StructuralGraph.
#
# StructuralGraph:
#     point -> point
#
# StructuralRelationGraph:
#     structural unit -> structural unit
#
# CPU only
# ============================================================


class StructuralRelationGraph:

    def __init__(
        self,
        near_threshold=1.5,
        contact_threshold=0.25,
        same_primitive=True
    ):

        self.near_threshold = float(
            near_threshold
        )

        self.contact_threshold = float(
            contact_threshold
        )

        self.same_primitive = bool(
            same_primitive
        )


    # --------------------------------------------------------
    # Generic value accessor
    # --------------------------------------------------------

    def _get_value(
        self,
        obj,
        name,
        default=None
    ):

        if isinstance(
            obj,
            dict
        ):

            return obj.get(
                name,
                default
            )

        if not hasattr(
            obj,
            name
        ):

            return default

        value = getattr(
            obj,
            name
        )

        if callable(value):

            value = value()

        return value


    # --------------------------------------------------------
    # Unit center
    # --------------------------------------------------------

    def _center(
        self,
        unit
    ):

        center = self._get_value(
            unit,
            "center",
            None
        )

        if center is not None:

            try:

                center = np.asarray(
                    center,
                    dtype=float
                ).reshape(-1)

                if center.size >= 3:

                    return center[:3]

            except Exception:

                pass


        points = self._get_value(
            unit,
            "points",
            None
        )

        if points is not None:

            points = np.asarray(
                points,
                dtype=float
            )

            if (
                points.ndim == 2
                and
                points.shape[1] >= 3
                and
                len(points) > 0
            ):

                return np.mean(
                    points[:, :3],
                    axis=0
                )


        return np.zeros(
            3,
            dtype=float
        )


    # --------------------------------------------------------
    # Primitive
    # --------------------------------------------------------

    def _primitive(
        self,
        unit
    ):

        return str(
            self._get_value(
                unit,
                "primitive",
                "unknown"
            )
        )


    # --------------------------------------------------------
    # Pairwise relation
    # --------------------------------------------------------

    def pair_relation(
        self,
        unit_a,
        unit_b
    ):

        ca = self._center(
            unit_a
        )

        cb = self._center(
            unit_b
        )

        distance = float(
            np.linalg.norm(
                ca - cb
            )
        )


        primitive_a = self._primitive(
            unit_a
        )

        primitive_b = self._primitive(
            unit_b
        )


        # ----------------------------------------------------
        # Same primitive type
        # ----------------------------------------------------

        if (
            self.same_primitive
            and
            primitive_a == primitive_b
        ):

            relation_type = "same"


        # ----------------------------------------------------
        # Contact
        # ----------------------------------------------------

        elif distance <= self.contact_threshold:

            relation_type = "contact"


        # ----------------------------------------------------
        # Near
        # ----------------------------------------------------

        elif distance <= self.near_threshold:

            relation_type = "near"


        # ----------------------------------------------------
        # Separate
        # ----------------------------------------------------

        else:

            relation_type = "separate"


        return {

            "source": None,

            "target": None,

            "units": None,

            "type":
                relation_type,

            "distance":
                distance,

            "primitive_source":
                primitive_a,

            "primitive_target":
                primitive_b

        }


    # --------------------------------------------------------
    # Build
    # --------------------------------------------------------

    def build(
        self,
        units
    ):

        relations = []

        N = len(
            units
        )


        for i in range(N):

            for j in range(
                i + 1,
                N
            ):

                relation = self.pair_relation(
                    units[i],
                    units[j]
                )


                relation[
                    "source"
                ] = i

                relation[
                    "target"
                ] = j

                relation[
                    "units"
                ] = [
                    i,
                    j
                ]


                relations.append(
                    relation
                )


        return relations


    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    def statistics(
        self,
        relations
    ):

        counts = {}


        for relation in relations:

            t = relation.get(
                "type",
                "unknown"
            )

            counts[t] = (
                counts.get(
                    t,
                    0
                )
                + 1
            )


        print(
            "\nStructural Relation Graph"
        )

        print(
            "Units:",
            len(
                {
                    x
                    for r in relations
                    for x in r.get(
                        "units",
                        []
                    )
                }
            )
        )

        print(
            "Relations:",
            len(
                relations
            )
        )

        for key in sorted(
            counts.keys()
        ):

            print(
                key + ":",
                counts[key]
            )


# ============================================================
# Compatibility aliases
# ============================================================

__all__ = [

    "StructuralGraph",

    "StructuralRelationGraph"

]
