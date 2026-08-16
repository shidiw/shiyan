# ============================================================
# Struct3D
# graph/relation.py
#
# Point-level Structural Graph Relation
#
# G = (V, E, W)
#
# Purpose:
#     Build local geometric relations between point nodes.
#
# Input:
#     points
#     normals
#     curvature
#
# Output:
#     edges
#     weights
#
# Invariance:
#     1. Translation invariant
#     2. Rotation invariant
#     3. Normal-orientation sign invariant
#     4. Point-order independent in geometric scale estimation
#
# CPU only
# ============================================================

import numpy as np


class StructuralGraph:
    """
    Struct3D Point-level Structural Relation Graph.

    G = (V, E, W)

    Each point is a graph node.

    An edge represents a local geometric relation between
    two neighboring points.

    Edge affinity is determined by:

        spatial discrepancy
        normal discrepancy
        curvature discrepancy

    The resulting graph is intended to encode local
    geometric continuity.
    """

    # ========================================================
    # Initialization
    # ========================================================

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

        self.sigma_n = float(
            sigma_n
        )

        self.sigma_k = float(
            sigma_k
        )

        self.alpha = float(
            alpha
        )

        self.beta = float(
            beta
        )

    # ========================================================
    # Characteristic Spatial Scale
    # ========================================================

    def estimate_sigma_x(
        self,
        points
    ):
        """
        Estimate a characteristic geometric scale.

        The scale is defined as the median distance among
        k-nearest-neighbor pairs.

        This is permutation invariant because it depends only
        on pairwise geometric distances and not on input order.

        Returns
        -------
        float
            Characteristic spatial scale.
        """

        points = np.asarray(
            points,
            dtype=float
        )

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

            # The first element corresponds to itself.
            d.sort()

            local = d[
                1:kk + 1
            ]

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
    # Normalize Normals
    # ========================================================

    def normalize_normals(
        self,
        normals
    ):
        """
        Normalize all normal vectors.

        Zero-length normals are kept numerically stable.
        """

        normals = np.asarray(
            normals,
            dtype=float
        )

        norm = np.linalg.norm(
            normals,
            axis=1,
            keepdims=True
        )

        return normals / np.maximum(
            norm,
            1e-12
        )

    # ========================================================
    # Build Graph
    # ========================================================

    def build(
        self,
        points,
        normals,
        curvature
    ):
        """
        Build the point-level structural graph.

        Parameters
        ----------
        points : (N, 3)
            Point coordinates.

        normals : (N, 3)
            Surface normals.

        curvature : (N,)
            Scalar curvature descriptor.

        Returns
        -------
        dict

            {
                "edges": (M, 2),
                "weights": (M,)
            }

        Notes
        -----

        The current implementation uses directed KNN edges:

            i -> j

        for each point i and its k nearest neighbors.

        Therefore the maximum number of edges is:

            N * k
        """

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

        if len(normals) != N:

            raise ValueError(
                "points and normals must have "
                "the same number of points"
            )

        if len(curvature) != N:

            raise ValueError(
                "points and curvature must have "
                "the same number of points"
            )

        # ----------------------------------------------------
        # Normalize normals
        # ----------------------------------------------------

        normals = self.normalize_normals(
            normals
        )

        # ----------------------------------------------------
        # Estimate characteristic spatial scale
        # ----------------------------------------------------

        if self.sigma_x is None:

            sigma_x = self.estimate_sigma_x(
                points
            )

        else:

            sigma_x = float(
                self.sigma_x
            )

        sigma_x = max(
            sigma_x,
            1e-12
        )

        # Store actual scale used by this graph.

        self.sigma_x = sigma_x

        edges = []
        weights = []

        # ====================================================
        # KNN graph
        # ====================================================

        kk = min(
            self.k,
            max(
                N - 1,
                0
            )
        )

        for i in range(N):

            # ------------------------------------------------
            # Pairwise distances from point i
            # ------------------------------------------------

            dist = np.linalg.norm(
                points - points[i],
                axis=1
            )

            # ------------------------------------------------
            # Stable sorting
            #
            # mergesort gives deterministic ordering when
            # distances are identical.
            # ------------------------------------------------

            neighbors = np.argsort(
                dist,
                kind="mergesort"
            )[1:kk + 1]

            for j in neighbors:

                j = int(j)

                weight = self.edge_weight(
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
                        j
                    ]
                )

                weights.append(
                    weight
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
    # Normal Distance
    # ========================================================

    def normal_distance(
        self,
        ni,
        nj
    ):
        """
        Orientation-independent normal discrepancy.

        Since surface normals estimated by PCA can arbitrarily
        flip sign,

            n ~ -n

        we use:

            d_n = 1 - |n_i · n_j|

        Therefore:

            n_i =  n_j  -> d_n = 0
            n_i = -n_j  -> d_n = 0

        This makes the relation invariant to normal orientation.
        """

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

        return float(
            1.0 - cosine
        )

    # ========================================================
    # Spatial Energy
    # ========================================================

    def spatial_energy(
        self,
        xi,
        xj
    ):
        """
        Normalized spatial discrepancy:

            E_x =
                ||x_i - x_j||^2
                ----------------
                    sigma_x^2
        """

        dx = np.linalg.norm(
            np.asarray(xi)
            -
            np.asarray(xj)
        )

        return float(
            dx * dx
            /
            (
                self.sigma_x ** 2
                +
                1e-12
            )
        )

    # ========================================================
    # Normal Energy
    # ========================================================

    def normal_energy(
        self,
        ni,
        nj
    ):
        """
        Normal discrepancy energy:

            E_n =
                alpha * d_n^2
                -------------
                   sigma_n^2
        """

        dn = self.normal_distance(
            ni,
            nj
        )

        return float(
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

    # ========================================================
    # Curvature Energy
    # ========================================================

    def curvature_energy(
        self,
        ki,
        kj
    ):
        """
        Curvature discrepancy energy:

            E_k =
                beta * (k_i-k_j)^2
                ------------------
                     sigma_k^2
        """

        dk = abs(
            float(ki)
            -
            float(kj)
        )

        return float(
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

    # ========================================================
    # Edge Weight
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
        """
        Compute structural affinity between two points.

        Total structural energy:

            E_ij =
                E_x
                +
                E_n
                +
                E_k

        Affinity:

            w_ij = exp(-E_ij)

        Therefore:

            0 < w_ij <= 1

        Large weight:
            geometrically similar local neighborhoods.

        Small weight:
            geometrically discontinuous neighborhoods.
        """

        # ----------------------------------------------------
        # Spatial
        # ----------------------------------------------------

        spatial = self.spatial_energy(
            xi,
            xj
        )

        # ----------------------------------------------------
        # Normal
        # ----------------------------------------------------

        normal = self.normal_energy(
            ni,
            nj
        )

        # ----------------------------------------------------
        # Curvature
        # ----------------------------------------------------

        curvature = self.curvature_energy(
            ki,
            kj
        )

        # ----------------------------------------------------
        # Total
        # ----------------------------------------------------

        energy = (
            spatial
            +
            normal
            +
            curvature
        )

        # ----------------------------------------------------
        # Affinity
        # ----------------------------------------------------

        weight = np.exp(
            -energy
        )

        return float(
            weight
        )

    # ========================================================
    # Statistics
    # ========================================================

    def statistics(
        self,
        graph
    ):
        """
        Print graph statistics.
        """

        edges = graph[
            "edges"
        ]

        weights = graph[
            "weights"
        ]

        print(
            "\nStructural Graph"
        )

        # ----------------------------------------------------
        # Node count
        # ----------------------------------------------------

        if len(edges) == 0:

            nodes = 0

        else:

            nodes = len(
                np.unique(
                    edges
                )
            )

        print(
            "Nodes:",
            nodes
        )

        # ----------------------------------------------------
        # Edge count
        # ----------------------------------------------------

        print(
            "Edges:",
            len(edges)
        )

        if len(weights) == 0:
            return

        # ----------------------------------------------------
        # Weight statistics
        # ----------------------------------------------------

        print(
            "Weight mean:",
            float(
                np.mean(
                    weights
                )
            )
        )

        print(
            "Weight std:",
            float(
                np.std(
                    weights
                )
            )
        )

        print(
            "Weight min:",
            float(
                np.min(
                    weights
                )
            )
        )

        print(
            "Weight max:",
            float(
                np.max(
                    weights
                )
            )
        )

        print(
            "Weight median:",
            float(
                np.median(
                    weights
                )
            )
        )

        # ----------------------------------------------------
        # Threshold statistics
        # ----------------------------------------------------

        for threshold in [
            0.01,
            0.05,
            0.1,
            0.2,
            0.5,
            0.8,
            0.9
        ]:

            ratio = np.mean(
                weights < threshold
            )

            print(
                f"Weight < {threshold}:",
                float(
                    ratio
                )
            )


# ============================================================
# Compatibility aliases
# ============================================================

GraphRelation = StructuralGraph
StructuralRelationGraph = StructuralGraph


__all__ = [
    "StructuralGraph",
    "GraphRelation",
    "StructuralRelationGraph"
]