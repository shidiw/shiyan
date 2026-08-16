import numpy as np


def estimate_curvature(
    eigenvalues
):

    eps=1e-12


    curvature = (
        eigenvalues[:,0]
        /
        (
        np.sum(
            eigenvalues,
            axis=1
        )
        +
        eps
        )
    )


    return curvature