import os
import numpy as np


# ============================================================
# Struct3D v2.0
# Structural Invariance Dataset Generator
#
# Generates:
#   sphere_original
#   sphere_translation
#   sphere_rotation
#   sphere_noise
#   sphere_partial
#   plane
#   cylinder
#
# Important:
# These variants represent the SAME structural object
# under different observations.
# ============================================================


OUTPUT_DIR = "data/invariance"

N = 1000

SEED = 42


# ============================================================
# Random
# ============================================================

rng = np.random.default_rng(SEED)


# ============================================================
# Sphere
# ============================================================

def generate_sphere(
    n=N,
    center=(0.0, 0.0, 0.0),
    radius=1.0
):

    center = np.asarray(
        center,
        dtype=float
    )

    phi = rng.uniform(
        0.0,
        2.0 * np.pi,
        n
    )

    cos_theta = rng.uniform(
        -1.0,
        1.0,
        n
    )

    theta = np.arccos(
        cos_theta
    )

    x = radius * np.sin(theta) * np.cos(phi)

    y = radius * np.sin(theta) * np.sin(phi)

    z = radius * np.cos(theta)


    points = np.stack(
        [x, y, z],
        axis=1
    )


    points += center


    return points


# ============================================================
# Rotation
# ============================================================

def rotation_matrix(
    rx,
    ry,
    rz
):

    cx = np.cos(rx)
    sx = np.sin(rx)

    cy = np.cos(ry)
    sy = np.sin(ry)

    cz = np.cos(rz)
    sz = np.sin(rz)


    Rx = np.array([
        [1, 0, 0],
        [0, cx, -sx],
        [0, sx, cx]
    ])


    Ry = np.array([
        [cy, 0, sy],
        [0, 1, 0],
        [-sy, 0, cy]
    ])


    Rz = np.array([
        [cz, -sz, 0],
        [sz, cz, 0],
        [0, 0, 1]
    ])


    return Rz @ Ry @ Rx


# ============================================================
# Plane
# ============================================================

def generate_plane(
    n=N,
    size=2.0
):

    x = rng.uniform(
        -size,
        size,
        n
    )

    y = rng.uniform(
        -size,
        size,
        n
    )

    z = np.zeros(n)


    return np.stack(
        [x, y, z],
        axis=1
    )


# ============================================================
# Cylinder
# ============================================================

def generate_cylinder(
    n=N,
    radius=1.0,
    height=2.0
):

    theta = rng.uniform(
        0.0,
        2.0 * np.pi,
        n
    )

    z = rng.uniform(
        -height / 2.0,
        height / 2.0,
        n
    )

    x = radius * np.cos(theta)

    y = radius * np.sin(theta)


    return np.stack(
        [x, y, z],
        axis=1
    )


# ============================================================
# Save
# ============================================================

def save(
    name,
    points
):

    path = os.path.join(
        OUTPUT_DIR,
        name + ".npy"
    )


    np.save(
        path,
        points
    )


    print(
        f"{name:25s}",
        points.shape,
        "->",
        path
    )


# ============================================================
# Main
# ============================================================

def main():

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )


    print()
    print(
        "Struct3D v2.0"
    )

    print(
        "Structural Invariance Dataset"
    )

    print(
        "Output:",
        OUTPUT_DIR
    )

    print()


    # --------------------------------------------------------
    # Original
    # --------------------------------------------------------

    sphere = generate_sphere()


    save(
        "sphere_original",
        sphere
    )


    # --------------------------------------------------------
    # Translation
    # --------------------------------------------------------

    sphere_translation = (
        sphere
        +
        np.array(
            [4.0, -3.0, 2.0]
        )
    )


    save(
        "sphere_translation",
        sphere_translation
    )


    # --------------------------------------------------------
    # Rotation
    # --------------------------------------------------------

    R = rotation_matrix(

        np.deg2rad(35),

        np.deg2rad(60),

        np.deg2rad(25)

    )


    sphere_rotation = (
        sphere @ R.T
    )


    save(
        "sphere_rotation",
        sphere_rotation
    )


    # --------------------------------------------------------
    # Noise
    # --------------------------------------------------------

    noise = rng.normal(
        0.0,
        0.03,
        sphere.shape
    )


    sphere_noise = (
        sphere
        +
        noise
    )


    save(
        "sphere_noise",
        sphere_noise
    )


    # --------------------------------------------------------
    # Partial Observation
    # --------------------------------------------------------

    keep = int(
        len(sphere) * 0.70
    )


    indices = rng.choice(
        len(sphere),
        keep,
        replace=False
    )


    sphere_partial = sphere[
        indices
    ]


    save(
        "sphere_partial",
        sphere_partial
    )


    # --------------------------------------------------------
    # Different structures
    # --------------------------------------------------------

    plane = generate_plane()


    save(
        "plane",
        plane
    )


    cylinder = generate_cylinder()


    save(
        "cylinder",
        cylinder
    )


    print()

    print(
        "Dataset generation complete."
    )


# ============================================================
# Entry
# ============================================================

if __name__ == "__main__":

    main()
