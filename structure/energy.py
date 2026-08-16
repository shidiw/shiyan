import numpy as np



class StructureEnergy:
    """
    Structural Energy Function

    E(U)=
        E_fit
        +
        lambda * E_complexity
        +
        gamma * E_boundary

    """



    def __init__(
        self,
        lambda_complexity=0.01,
        gamma_boundary=0.01
    ):


        self.lambda_complexity = (
            lambda_complexity
        )

        self.gamma_boundary = (
            gamma_boundary
        )



    def compute(
        self,
        unit
    ):
        """
        Compute total structural energy

        """

        fit = self.fit_energy(
            unit
        )


        complexity = (
            self.complexity_energy(
                unit
            )
        )


        boundary = (
            self.boundary_energy(
                unit
            )
        )



        total = (

            fit

            +

            self.lambda_complexity
            *
            complexity

            +

            self.gamma_boundary
            *
            boundary

        )


        unit.energy = total


        return {

            "total":
                total,

            "fit":
                fit,

            "complexity":
                complexity,

            "boundary":
                boundary
        }



    # ==================================================
    # Geometry fitting energy
    # ==================================================


    def fit_energy(
        self,
        unit
    ):


        primitive = unit.primitive


        points = unit.points



        if primitive == "plane":

            return self.plane_fit(
                points,
                unit.parameters
            )


        elif primitive == "sphere":

            return self.sphere_fit(
                points,
                unit.parameters
            )


        elif primitive == "cylinder":

            return self.cylinder_fit(
                points,
                unit.parameters
            )


        return 0.0



    # --------------------------
    # Plane
    # --------------------------

    def plane_fit(
        self,
        points,
        params
    ):


        n = params["normal"]

        d = params["d"]



        distance = np.abs(

            points @ n

            +

            d

        )


        return np.mean(
            distance ** 2
        )



    # --------------------------
    # Sphere
    # --------------------------

    def sphere_fit(
        self,
        points,
        params
    ):


        c = params["center"]

        r = params["radius"]



        distance = np.linalg.norm(
            points-c,
            axis=1
        )



        residual = (
            distance-r
        )


        return np.mean(
            residual ** 2
        )



    # --------------------------
    # Cylinder
    # --------------------------

    def cylinder_fit(
        self,
        points,
        params
    ):


        c=params["center"]


        radius=params["radius"]



        xy = points[:,:2]


        center_xy=c[:2]



        distance=np.linalg.norm(

            xy-center_xy,

            axis=1

        )



        residual = (
            distance-radius
        )



        return np.mean(
            residual**2
        )




    # ==================================================
    # Complexity Energy
    # ==================================================

    def complexity_energy(
        self,
        unit
    ):


        primitive_dimension={

            "plane":4,

            "sphere":4,

            "cylinder":5

        }



        return primitive_dimension.get(
            unit.primitive,
            10
        )



    # ==================================================
    # Boundary Energy
    # ==================================================

    def boundary_energy(
        self,
        unit
    ):

        """
        First version:

        measure point dispersion

        Later replaced by graph boundary

        """


        points=unit.points


        center=np.mean(
            points,
            axis=0
        )


        spread=np.linalg.norm(

            points-center,

            axis=1

        )


        return np.var(
            spread
        )