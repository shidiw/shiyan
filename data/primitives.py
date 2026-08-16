import numpy as np



# ==================================================
# Plane
# ==================================================

def generate_plane(n=1000):

    x = np.random.uniform(
        -1,
        1,
        n
    )


    y = np.random.uniform(
        -1,
        1,
        n
    )


    z = np.zeros(n)



    points = np.stack(
        [
            x,
            y,
            z
        ],
        axis=1
    )


    return points




# ==================================================
# Sphere
# ==================================================

def generate_sphere(n=1000):


    theta = np.random.uniform(
        0,
        np.pi,
        n
    )


    phi = np.random.uniform(
        0,
        2*np.pi,
        n
    )


    r = 1.0



    x = r*np.sin(theta)*np.cos(phi)

    y = r*np.sin(theta)*np.sin(phi)

    z = r*np.cos(theta)



    points = np.stack(
        [
            x,
            y,
            z
        ],
        axis=1
    )


    # move sphere center

    points += np.array(
        [
            3,
            0,
            0
        ]
    )


    return points





# ==================================================
# Cylinder
# ==================================================

def generate_cylinder(n=1000):


    theta = np.random.uniform(
        0,
        2*np.pi,
        n
    )


    z = np.random.uniform(
        -1,
        1,
        n
    )


    r = 1.0



    x = r*np.cos(theta)

    y = r*np.sin(theta)



    points = np.stack(
        [
            x,
            y,
            z
        ],
        axis=1
    )


    # move cylinder center

    points += np.array(
        [
            -3,
            0,
            0
        ]
    )


    return points





# ==================================================
# Dataset Generator
# ==================================================

def generate_dataset(
    n_plane=1000,
    n_sphere=1000,
    n_cylinder=1000
):


    plane = generate_plane(
        n_plane
    )


    sphere = generate_sphere(
        n_sphere
    )


    cylinder = generate_cylinder(
        n_cylinder
    )



    points = np.concatenate(
        [
            plane,
            sphere,
            cylinder
        ],
        axis=0
    )



    labels = np.concatenate(
        [
            np.zeros(
                n_plane,
                dtype=np.int32
            ),


            np.ones(
                n_sphere,
                dtype=np.int32
            ),


            np.ones(
                n_cylinder,
                dtype=np.int32
            )*2
        ]
    )



    return points, labels





# ==================================================
# Main
# ==================================================

if __name__ == "__main__":


    points, labels = generate_dataset()



    np.save(
        "primitives.npy",
        points
    )


    np.save(
        "primitives_labels.npy",
        labels
    )


    print(
        "Saved primitives.npy"
    )


    print(
        "Points:",
        points.shape
    )


    print(
        "Labels:",
        labels.shape
    )


    print("\nStatistics")


    print(
        "Plane:",
        np.sum(labels==0)
    )


    print(
        "Sphere:",
        np.sum(labels==1)
    )


    print(
        "Cylinder:",
        np.sum(labels==2)
    )