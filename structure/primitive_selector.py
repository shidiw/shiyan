import numpy as np



class PrimitiveSelector:
    """
    Struct3D Primitive Discovery


    Optimize:

        P*=argmin(Efit + λC)


    primitives:

        plane
        sphere
        cylinder

    """



    def __init__(
        self,
        complexity_weight=0.01
    ):

        self.lambda_c = complexity_weight


        self.complexity = {

            "plane":4,

            "sphere":4,

            "cylinder":5

        }




    def predict(
        self,
        unit
    ):


        points = unit.points


        candidates={}


        candidates["plane"] = self.fit_plane(points)

        candidates["sphere"] = self.fit_sphere(points)

        candidates["cylinder"] = self.fit_cylinder(points)



        for name in candidates:


            candidates[name]["total_energy"] = (

                candidates[name]["energy"]

                +

                self.lambda_c *
                self.complexity[name]

            )



        best=min(

            candidates.items(),

            key=lambda x:
            x[1]["total_energy"]

        )



        return {

            "primitive":best[0],

            "parameters":
                best[1]["parameters"],

            "energy":
                best[1]["total_energy"],

            "fit_energy":
                best[1]["energy"],

            "candidates":
                candidates

        }




    # ===============================
    # Plane
    # ===============================

    def fit_plane(
        self,
        points
    ):


        center=np.mean(
            points,
            axis=0
        )


        X=points-center


        _,_,V=np.linalg.svd(
            X
        )


        normal=V[-1]


        d=-np.dot(
            normal,
            center
        )


        residual=np.abs(

            points@normal+d

        )


        energy=np.mean(
            residual**2
        )


        return {


            "parameters":

            {

            "normal":normal,

            "d":d

            },


            "energy":energy

        }





    # ===============================
    # Sphere
    # ===============================

    def fit_sphere(
        self,
        points
    ):


        center=np.mean(
            points,
            axis=0
        )


        radius=np.mean(

            np.linalg.norm(

                points-center,

                axis=1

            )

        )


        residual=(

            np.linalg.norm(

                points-center,

                axis=1

            )
            -
            radius

        )


        energy=np.mean(
            residual**2
        )



        return {


            "parameters":

            {

            "center":center,

            "radius":radius

            },


            "energy":energy

        }





    # ===============================
    # Cylinder
    # ===============================

    def fit_cylinder(
        self,
        points
    ):


        center=np.mean(
            points,
            axis=0
        )


        X=points-center



        cov=np.cov(
            X.T
        )


        eigvals,eigvecs=np.linalg.eigh(
            cov
        )



        axis=eigvecs[

            :,

            np.argmax(eigvals)

        ]



        axis/=(
            np.linalg.norm(axis)
            +
            1e-12
        )



        cross=np.cross(
            X,
            axis
        )


        distance=np.linalg.norm(
            cross,
            axis=1
        )



        radius=np.mean(
            distance
        )



        residual=distance-radius


        energy=np.mean(
            residual**2
        )



        return {


            "parameters":

            {

            "center":center,

            "axis":axis,

            "radius":radius

            },


            "energy":energy

        }