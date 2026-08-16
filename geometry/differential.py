import numpy as np
from sklearn.neighbors import NearestNeighbors


class DifferentialGeometry:


    def __init__(
        self,
        points,
        k=30
    ):
        self.points = points
        self.k = k


    def neighborhood(self):

        nbrs = NearestNeighbors(
            n_neighbors=self.k
        )

        nbrs.fit(self.points)

        _, indices = nbrs.kneighbors(
            self.points
        )

        return indices



    def covariance(
        self,
        idx
    ):

        neighbors = self.points[idx]

        center = np.mean(
            neighbors,
            axis=0
        )

        X = neighbors - center

        C = (
            X.T @ X
            /
            len(idx)
        )

        return C



    def eigen_analysis(self):

        indices = self.neighborhood()


        eigenvalues = []

        eigenvectors = []


        for idx in indices:

            C = self.covariance(idx)


            w,v = np.linalg.eigh(C)


            order=np.argsort(w)


            w=w[order]

            v=v[:,order]


            eigenvalues.append(w)

            eigenvectors.append(v)


        return (
            np.array(eigenvalues),
            np.array(eigenvectors)
        )