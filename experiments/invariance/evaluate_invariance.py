# -*- coding: utf-8 -*-

"""
Struct3D
========================================================

Geometry Field Invariance / Equivariance Evaluation
Version: v2.0

This experiment verifies:

1. Rotation invariance
2. Rotation equivariance of normals
3. Translation invariance
4. Scale behavior
5. Permutation invariance

Mathematical target
-------------------

Scalar geometric descriptors:

    I(RX + t) = I(X)

Vector geometric descriptors:

    n(RX + t) = R n(X)

For covariance eigenvalues:

    lambda(sX) = s^2 lambda(X)

Therefore raw eigenvalues are NOT scale invariant.

Normalized eigenvalues:

    lambda_hat_i =
        lambda_i / sum_j lambda_j

are scale invariant.

========================================================
"""

import os
import sys
import glob
import numpy as np


# ============================================================
# Project Root
# ============================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        CURRENT_DIR,
        "../.."
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(
        0,
        PROJECT_ROOT
    )


# ============================================================
# Geometry Field
# ============================================================

from geometry.field import GeometryField


# ============================================================
# Numerical Configuration
# ============================================================

EPS = 1e-12

RANDOM_SEED = 42

DEFAULT_K = 15

SCALE_FACTOR = 2.0


# ============================================================
# Utility
# ============================================================

def banner(
    text
):

    print()
    print("=" * 56)
    print(text)
    print("=" * 56)


# ============================================================
# Deterministic Test Cloud
# ============================================================

def generate_test_cloud(
    seed=RANDOM_SEED
):
    """
    Generate a deterministic point cloud.

    Structure:

        1000 plane points
        1000 sphere points
        1000 sphere points

    Total:

        3000 points
    """

    rng = np.random.default_rng(
        seed
    )

    # --------------------------------------------------------
    # Plane
    # --------------------------------------------------------

    n_plane = 1000

    x = rng.uniform(
        -1.5,
        1.5,
        n_plane
    )

    y = rng.uniform(
        -1.5,
        1.5,
        n_plane
    )

    z = np.zeros(
        n_plane
    )

    plane = np.column_stack(
        [
            x,
            y,
            z
        ]
    )


    # --------------------------------------------------------
    # Sphere 1
    # --------------------------------------------------------

    n_sphere_1 = 1000

    center_1 = np.array(
        [
            -3.0,
            0.0,
            0.0
        ],
        dtype=np.float64
    )

    radius_1 = 1.0

    u = rng.uniform(
        0.0,
        1.0,
        n_sphere_1
    )

    v = rng.uniform(
        0.0,
        1.0,
        n_sphere_1
    )

    theta = (
        2.0 *
        np.pi *
        u
    )

    phi = np.arccos(
        2.0 * v - 1.0
    )

    xs = (
        np.sin(phi)
        *
        np.cos(theta)
    )

    ys = (
        np.sin(phi)
        *
        np.sin(theta)
    )

    zs = np.cos(
        phi
    )

    sphere_1 = np.column_stack(
        [
            xs,
            ys,
            zs
        ]
    )

    sphere_1 *= radius_1

    sphere_1 += center_1


    # --------------------------------------------------------
    # Sphere 2
    # --------------------------------------------------------

    n_sphere_2 = 1000

    center_2 = np.array(
        [
            3.0,
            0.0,
            0.0
        ],
        dtype=np.float64
    )

    radius_2 = 1.0

    u = rng.uniform(
        0.0,
        1.0,
        n_sphere_2
    )

    v = rng.uniform(
        0.0,
        1.0,
        n_sphere_2
    )

    theta = (
        2.0 *
        np.pi *
        u
    )

    phi = np.arccos(
        2.0 * v - 1.0
    )

    xs = (
        np.sin(phi)
        *
        np.cos(theta)
    )

    ys = (
        np.sin(phi)
        *
        np.sin(theta)
    )

    zs = np.cos(
        phi
    )

    sphere_2 = np.column_stack(
        [
            xs,
            ys,
            zs
        ]
    )

    sphere_2 *= radius_2

    sphere_2 += center_2


    # --------------------------------------------------------
    # Combine
    # --------------------------------------------------------

    points = np.vstack(
        [
            plane,
            sphere_1,
            sphere_2
        ]
    )

    return points


# ============================================================
# Load Point Cloud
# ============================================================

def load_ply_points(
    path
):

    try:

        import open3d as o3d

    except Exception:

        return None


    try:

        cloud = o3d.io.read_point_cloud(
            path
        )

        points = np.asarray(
            cloud.points,
            dtype=np.float64
        )

        if len(points) == 0:
            return None

        return points

    except Exception:

        return None


# ============================================================
# Find Point Cloud
# ============================================================

def find_point_cloud():

    candidates = [

        "data/test.ply",

        "data/sample.ply",

        "data/pointcloud.ply",

        "test.ply",

        "../test.ply",

        "../../test.ply",

    ]


    for path in candidates:

        if os.path.exists(path):

            points = load_ply_points(
                path
            )

            if points is not None:

                print(
                    "Using point cloud:",
                    path
                )

                return points


    # Search project tree

    patterns = [

        os.path.join(
            PROJECT_ROOT,
            "**",
            "*.ply"
        ),

        os.path.join(
            PROJECT_ROOT,
            "**",
            "*.PLY"
        )

    ]


    found = []

    for pattern in patterns:

        found.extend(
            glob.glob(
                pattern,
                recursive=True
            )
        )


    for path in found:

        points = load_ply_points(
            path
        )

        if points is not None:

            print(
                "Using point cloud:",
                path
            )

            return points


    return None


# ============================================================
# Rotation Matrix
# ============================================================

def rotation_matrix_xyz(
    rx,
    ry,
    rz
):
    """
    Rotation:

        R = Rz Ry Rx
    """

    cx = np.cos(rx)
    sx = np.sin(rx)

    cy = np.cos(ry)
    sy = np.sin(ry)

    cz = np.cos(rz)
    sz = np.sin(rz)


    Rx = np.array(
        [
            [1, 0, 0],
            [0, cx, -sx],
            [0, sx, cx]
        ],
        dtype=np.float64
    )


    Ry = np.array(
        [
            [cy, 0, sy],
            [0, 1, 0],
            [-sy, 0, cy]
        ],
        dtype=np.float64
    )


    Rz = np.array(
        [
            [cz, -sz, 0],
            [sz, cz, 0],
            [0, 0, 1]
        ],
        dtype=np.float64
    )


    return (
        Rz
        @
        Ry
        @
        Rx
    )


# ============================================================
# Transform
# ============================================================

def transform_points(
    points,
    R=None,
    t=None,
    scale=1.0
):

    X = np.asarray(
        points,
        dtype=np.float64
    )

    X = X * scale


    if R is not None:

        X = X @ R.T


    if t is not None:

        X = X + t


    return X


# ============================================================
# Compute Geometry
# ============================================================

def compute_geometry(
    points,
    k=DEFAULT_K
):

    field = GeometryField(
        points,
        k=k
    )

    result = field.compute()

    return result


# ============================================================
# Normalized Eigenvalues
# ============================================================

def normalized_eigenvalues(
    eigenvalues
):

    eigenvalues = np.asarray(
        eigenvalues,
        dtype=np.float64
    )


    total = np.sum(
        eigenvalues,
        axis=1,
        keepdims=True
    )


    return (
        eigenvalues
        /
        (
            total
            +
            EPS
        )
    )


# ============================================================
# Normal Statistics
# ============================================================

def normal_alignment(
    n1,
    n2
):
    """
    Compare two normal fields directly.

    Because PCA normals have sign ambiguity:

        n
        and
        -n

    represent the same unoriented normal.

    Therefore use:

        |n1 dot n2|
    """

    n1 = np.asarray(
        n1,
        dtype=np.float64
    )

    n2 = np.asarray(
        n2,
        dtype=np.float64
    )


    dots = np.sum(
        n1 * n2,
        axis=1
    )


    dots = np.clip(
        np.abs(dots),
        0.0,
        1.0
    )


    return {

        "mean":
            float(
                np.mean(dots)
            ),

        "std":
            float(
                np.std(dots)
            ),

        "min":
            float(
                np.min(dots)
            ),

    }


# ============================================================
# Normal Equivariance
# ============================================================

def normal_equivariance(
    original_normals,
    transformed_normals,
    R
):
    """
    Correct rotation test for normals.

    The expected relationship is:

        n(RX) = R n(X)

    NOT:

        n(RX) = n(X)

    Because normals are unoriented, use:

        | dot(R n, n') |
    """

    original_normals = np.asarray(
        original_normals,
        dtype=np.float64
    )

    transformed_normals = np.asarray(
        transformed_normals,
        dtype=np.float64
    )


    # Transform original normals

    predicted = (
        original_normals
        @
        R.T
    )


    dots = np.sum(
        predicted
        *
        transformed_normals,
        axis=1
    )


    dots = np.clip(
        np.abs(dots),
        0.0,
        1.0
    )


    errors = (
        1.0
        -
        dots
    )


    return {

        "mean_alignment":
            float(
                np.mean(dots)
            ),

        "std_alignment":
            float(
                np.std(dots)
            ),

        "min_alignment":
            float(
                np.min(dots)
            ),

        "mean_error":
            float(
                np.mean(errors)
            ),

        "max_error":
            float(
                np.max(errors)
            )

    }


# ============================================================
# Compare Scalar
# ============================================================

def scalar_error(
    a,
    b
):

    a = np.asarray(
        a,
        dtype=np.float64
    )

    b = np.asarray(
        b,
        dtype=np.float64
    )


    return float(
        np.mean(
            np.abs(
                a - b
            )
        )
    )


# ============================================================
# Original Geometry
# ============================================================

def evaluate_original(
    geometry
):

    normals = geometry[
        "normals"
    ]

    curvature = geometry[
        "curvature"
    ]

    eigenvalues = geometry[
        "eigenvalues"
    ]

    normalized = normalized_eigenvalues(
        eigenvalues
    )


    print()

    print(
        "Original"
    )


    print(
        "Normal norm mean:",
        np.mean(
            np.linalg.norm(
                normals,
                axis=1
            )
        )
    )


    print(
        "Normal norm std:",
        np.std(
            np.linalg.norm(
                normals,
                axis=1
            )
        )
    )


    print(
        "Curvature mean:",
        np.mean(
            curvature
        )
    )


    print(
        "Curvature std:",
        np.std(
            curvature
        )
    )


    print(
        "Eigenvalue mean:",
        np.mean(
            eigenvalues,
            axis=0
        )
    )


    print(
        "Eigenvalue std:",
        np.std(
            eigenvalues,
            axis=0
        )
    )


    print(
        "Normalized eigenvalue mean:",
        np.mean(
            normalized,
            axis=0
        )
    )


    print(
        "Normalized eigenvalue std:",
        np.std(
            normalized,
            axis=0
        )
    )


# ============================================================
# Rotation Test
# ============================================================

def evaluate_rotation(
    original,
    rotated,
    R
):

    banner(
        "[2] Rotation Invariance / Equivariance"
    )


    curvature_error = scalar_error(
        original["curvature"],
        rotated["curvature"]
    )


    eig_original = normalized_eigenvalues(
        original["eigenvalues"]
    )

    eig_rotated = normalized_eigenvalues(
        rotated["eigenvalues"]
    )


    eigen_error = scalar_error(
        eig_original,
        eig_rotated
    )


    normal_stats = normal_equivariance(
        original["normals"],
        rotated["normals"],
        R
    )


    print(
        "Curvature error:",
        curvature_error
    )


    print(
        "Normalized eigenvalue error:",
        eigen_error
    )


    print(
        "Normal equivariance:"
    )

    print(
        normal_stats
    )


    return {

        "curvature":
            curvature_error,

        "normalized_eigenvalues":
            eigen_error,

        "normal":
            normal_stats

    }


# ============================================================
# Translation Test
# ============================================================

def evaluate_translation(
    original,
    translated
):

    banner(
        "[3] Translation Invariance"
    )


    curvature_error = scalar_error(
        original["curvature"],
        translated["curvature"]
    )


    eig_original = normalized_eigenvalues(
        original["eigenvalues"]
    )

    eig_translated = normalized_eigenvalues(
        translated["eigenvalues"]
    )


    eigen_error = scalar_error(
        eig_original,
        eig_translated
    )


    normal_stats = normal_alignment(
        original["normals"],
        translated["normals"]
    )


    print(
        "Curvature error:",
        curvature_error
    )


    print(
        "Normalized eigenvalue error:",
        eigen_error
    )


    print(
        "Normal alignment:",
        normal_stats
    )


    return {

        "curvature":
            curvature_error,

        "normalized_eigenvalues":
            eigen_error,

        "normal":
            normal_stats

    }


# ============================================================
# Scale Test
# ============================================================

def evaluate_scale(
    original,
    scaled,
    scale
):

    banner(
        "[4] Scale Test"
    )


    # --------------------------------------------------------
    # Curvature
    # --------------------------------------------------------

    curvature_error = scalar_error(
        original["curvature"],
        scaled["curvature"]
    )


    # --------------------------------------------------------
    # Normalized Eigenvalues
    # --------------------------------------------------------

    eig_original = normalized_eigenvalues(
        original["eigenvalues"]
    )

    eig_scaled = normalized_eigenvalues(
        scaled["eigenvalues"]
    )


    normalized_error = scalar_error(
        eig_original,
        eig_scaled
    )


    # --------------------------------------------------------
    # Raw Eigenvalue Scaling
    #
    # lambda(sX) = s^2 lambda(X)
    # --------------------------------------------------------

    expected = (
        original["eigenvalues"]
        *
        scale**2
    )


    raw_error = scalar_error(
        expected,
        scaled["eigenvalues"]
    )


    # --------------------------------------------------------
    # Normal
    # --------------------------------------------------------

    normal_stats = normal_alignment(
        original["normals"],
        scaled["normals"]
    )


    print(
        "Scale factor:",
        scale
    )


    print(
        "Curvature error:",
        curvature_error
    )


    print(
        "Normalized eigenvalue error:",
        normalized_error
    )


    print(
        "Raw eigenvalue scaling error:",
        raw_error
    )


    print(
        "Normal alignment:",
        normal_stats
    )


    return {

        "curvature":
            curvature_error,

        "normalized_eigenvalues":
            normalized_error,

        "raw_eigenvalue_scaling":
            raw_error,

        "normal":
            normal_stats

    }


# ============================================================
# Permutation Test
# ============================================================

def evaluate_permutation(
    points,
    original
):

    banner(
        "[5] Permutation Invariance"
    )


    rng = np.random.default_rng(
        RANDOM_SEED
    )


    permutation = rng.permutation(
        len(points)
    )


    shuffled_points = points[
        permutation
    ]


    shuffled = compute_geometry(
        shuffled_points
    )


    # --------------------------------------------------------
    # Restore original order
    # --------------------------------------------------------

    inverse = np.argsort(
        permutation
    )


    shuffled_curvature = (
        shuffled["curvature"]
        [inverse]
    )


    shuffled_eigenvalues = (
        shuffled["eigenvalues"]
        [inverse]
    )


    shuffled_normals = (
        shuffled["normals"]
        [inverse]
    )


    # --------------------------------------------------------
    # Compare
    # --------------------------------------------------------

    curvature_error = scalar_error(
        original["curvature"],
        shuffled_curvature
    )


    eig_original = normalized_eigenvalues(
        original["eigenvalues"]
    )

    eig_shuffled = normalized_eigenvalues(
        shuffled_eigenvalues
    )


    eigen_error = scalar_error(
        eig_original,
        eig_shuffled
    )


    normal_stats = normal_alignment(
        original["normals"],
        shuffled_normals
    )


    print(
        "Curvature error:",
        curvature_error
    )


    print(
        "Normalized eigenvalue error:",
        eigen_error
    )


    print(
        "Normal alignment:",
        normal_stats
    )


    return {

        "curvature":
            curvature_error,

        "normalized_eigenvalues":
            eigen_error,

        "normal":
            normal_stats

    }


# ============================================================
# Invariance Evaluation
# ============================================================

def evaluate(
    points,
    k=DEFAULT_K
):

    banner(
        "Struct3D Invariance Evaluation v2"
    )


    print(
        "Input:",
        points.shape
    )


    # ========================================================
    # Original
    # ========================================================

    banner(
        "[1] Original Geometry Field"
    )


    original = compute_geometry(
        points,
        k=k
    )


    evaluate_original(
        original
    )


    # ========================================================
    # Rotation
    # ========================================================

    R = rotation_matrix_xyz(
        np.deg2rad(37.0),
        np.deg2rad(-23.0),
        np.deg2rad(51.0)
    )


    rotated_points = transform_points(
        points,
        R=R
    )


    rotated = compute_geometry(
        rotated_points,
        k=k
    )


    rotation_result = evaluate_rotation(
        original,
        rotated,
        R
    )


    # ========================================================
    # Translation
    # ========================================================

    translation = np.array(
        [
            10.0,
            -7.0,
            4.5
        ],
        dtype=np.float64
    )


    translated_points = transform_points(
        points,
        t=translation
    )


    translated = compute_geometry(
        translated_points,
        k=k
    )


    translation_result = evaluate_translation(
        original,
        translated
    )


    # ========================================================
    # Scale
    # ========================================================

    scaled_points = transform_points(
        points,
        scale=SCALE_FACTOR
    )


    scaled = compute_geometry(
        scaled_points,
        k=k
    )


    scale_result = evaluate_scale(
        original,
        scaled,
        SCALE_FACTOR
    )


    # ========================================================
    # Permutation
    # ========================================================

    permutation_result = evaluate_permutation(
        points,
        original
    )


    # ========================================================
    # Summary
    # ========================================================

    banner(
        "Invariance Summary"
    )


    print()
    print(
        "Rotation:"
    )

    print(
        "  curvature:",
        rotation_result[
            "curvature"
        ]
    )

    print(
        "  normalized eigenvalues:",
        rotation_result[
            "normalized_eigenvalues"
        ]
    )

    print(
        "  normal equivariance:",
        rotation_result[
            "normal"
        ]
    )


    print()
    print(
        "Translation:"
    )

    print(
        "  curvature:",
        translation_result[
            "curvature"
        ]
    )

    print(
        "  normalized eigenvalues:",
        translation_result[
            "normalized_eigenvalues"
        ]
    )

    print(
        "  normal:",
        translation_result[
            "normal"
        ]
    )


    print()
    print(
        "Scale:"
    )

    print(
        "  curvature:",
        scale_result[
            "curvature"
        ]
    )

    print(
        "  normalized eigenvalues:",
        scale_result[
            "normalized_eigenvalues"
        ]
    )

    print(
        "  raw eigenvalue scaling:",
        scale_result[
            "raw_eigenvalue_scaling"
        ]
    )

    print(
        "  normal:",
        scale_result[
            "normal"
        ]
    )


    print()
    print(
        "Permutation:"
    )

    print(
        "  curvature:",
        permutation_result[
            "curvature"
        ]
    )

    print(
        "  normalized eigenvalues:",
        permutation_result[
            "normalized_eigenvalues"
        ]
    )

    print(
        "  normal:",
        permutation_result[
            "normal"
        ]
    )


    # ========================================================
    # Final Interpretation
    # ========================================================

    banner(
        "Interpretation"
    )


    print(
        "Scalar geometry:"
    )

    print(
        "  curvature / surface variation -> invariant"
    )

    print(
        "  normalized eigenvalues -> invariant"
    )


    print()

    print(
        "Vector geometry:"
    )

    print(
        "  normal -> rotation equivariant"
    )


    print()

    print(
        "Scale:"
    )

    print(
        "  raw eigenvalues scale as s^2"
    )

    print(
        "  normalized eigenvalues are scale invariant"
    )


    print()

    print(
        "This establishes the Struct3D geometry-field"
    )

    print(
        "invariant/equivariant decomposition."
    )


    return {

        "original":
            original,

        "rotation":
            rotation_result,

        "translation":
            translation_result,

        "scale":
            scale_result,

        "permutation":
            permutation_result

    }


# ============================================================
# Main
# ============================================================

def main():

    points = find_point_cloud()


    if points is None:

        print(
            "No point cloud file found."
        )

        print(
            "Generating deterministic test cloud."
        )

        points = generate_test_cloud()


    points = np.asarray(
        points,
        dtype=np.float64
    )


    # --------------------------------------------------------
    # Remove invalid points
    # --------------------------------------------------------

    valid = np.all(
        np.isfinite(points),
        axis=1
    )


    if not np.all(valid):

        points = points[
            valid
        ]


    # --------------------------------------------------------
    # Basic validation
    # --------------------------------------------------------

    if points.ndim != 2:

        raise ValueError(
            "Point cloud must have shape (N, 3)."
        )


    if points.shape[1] != 3:

        raise ValueError(
            "Point cloud must have shape (N, 3)."
        )


    if len(points) < 20:

        raise ValueError(
            "Point cloud contains too few points."
        )


    evaluate(
        points,
        k=DEFAULT_K
    )


# ============================================================
# Entry
# ============================================================

if __name__ == "__main__":

    main()