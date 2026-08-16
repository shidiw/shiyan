import numpy as np



class GeometryField:
    """
    Geometry Field

    Extract local geometric invariants:

    normal
    curvature
    eigen spectrum

    """


    def __init__(
        self,
        points,
        k=15
    ):

        self.points = points

        self.k = k



    # ======================================
    # Main API
    # ======================================

    def compute(self):


        normals = []

        curvature = []

        eigenvalues = []



        N=len(
            self.points
        )


        for i in range(N):


            p=self.points[i]



            # nearest neighbors

            dist=np.linalg.norm(

                self.points-p,

                axis=1

            )


            idx=np.argsort(
                dist
            )[1:self.k+1]



            neighbors=self.points[idx]



            # covariance


            X=neighbors-np.mean(
                neighbors,
                axis=0
            )


            cov=np.dot(
                X.T,
                X
            ) / len(neighbors)



            eigvals,eigvecs=np.linalg.eigh(
                cov
            )


            order=np.argsort(
                eigvals
            )


            eigvals=eigvals[order]

            eigvecs=eigvecs[:,order]



            # smallest eigenvector

            normal=eigvecs[:,0]


            normals.append(
                normal
            )


            # surface variation curvature

            curv=(

                eigvals[0]

                /

                (
                np.sum(eigvals)
                +
                1e-12
                )

            )


            curvature.append(
                curv
            )


            eigenvalues.append(
                eigvals
            )



        return {

            "normals":
                np.asarray(
                    normals
                ),


            "curvature":
                np.asarray(
                    curvature
                ),


            "eigenvalues":
                np.asarray(
                    eigenvalues
                )

        }