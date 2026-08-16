import numpy as np



class StructuralUnit:
    """
    Structural Unit

    U_k = (P_k, theta_k, E_k)

    P_k:
        points belonging to structure

    theta_k:
        primitive parameters

    E_k:
        structural energy

    """


    def __init__(
        self,
        points,
        primitive,
        indices=None
    ):

        self.points = points

        self.primitive = primitive

        self.indices = indices


        self.parameters = {}

        self.energy = None



    # ==========================================
    # Basic information
    # ==========================================


    def size(self):

        return len(
            self.points
        )



    def center(self):

        return np.mean(
            self.points,
            axis=0
        )



    def info(self):

        return {

            "primitive":
                self.primitive,


            "points":
                self.size(),


            "center":
                self.center(),


            "energy":
                self.energy

        }



    # ==========================================
    # Primitive fitting
    # ==========================================


    def estimate_parameters(self):


        if self.primitive == "plane":

            self.parameters = (
                self.fit_plane()
            )


        elif self.primitive == "sphere":

            self.parameters = (
                self.fit_sphere()
            )


        elif self.primitive == "cylinder":

            self.parameters = (
                self.fit_cylinder()
            )



    # ==========================================
    # Plane fitting
    #
    # x*n+d=0
    #
    # ==========================================


    def fit_plane(self):


        P=self.points


        center=np.mean(
            P,
            axis=0
        )


        X=P-center


        _,_,V=np.linalg.svd(
            X
        )


        normal=V[-1]


        d=-np.dot(
            normal,
            center
        )



        return {

            "normal":
                normal,


            "d":
                d

        }



    # ==========================================
    # Sphere fitting
    #
    # ||x-c||^2=r^2
    #
    # ==========================================


    def fit_sphere(self):


        P=self.points



        #
        # equation:
        #
        # 2cx*x+
        # 2cy*y+
        # 2cz*z+
        # alpha
        #
        # =
        #
        # x^2+y^2+z^2
        #


        A=np.concatenate(

            [
                2*P,

                np.ones(
                    (
                    len(P),
                    1
                    )
                )

            ],

            axis=1

        )


        b=np.sum(
            P*P,
            axis=1
        )



        solution,_,_,_=np.linalg.lstsq(
            A,
            b,
            rcond=None
        )


        center=solution[:3]


        alpha=solution[3]



        radius=np.sqrt(

            np.sum(
                center**2
            )

            +

            alpha

        )



        return {

            "center":
                center,


            "radius":
                radius

        }



    # ==========================================
    # Cylinder fitting
    #
    # Axis aligned cylinder
    #
    # ==========================================


    def fit_cylinder(self):


        P=self.points



        xy=P[:,:2]



        #
        # circle fitting
        #
        # x^2+y^2+Ax+By+C=0
        #


        A=np.concatenate(

            [

                xy,

                np.ones(
                    (
                    len(xy),
                    1
                    )
                )

            ],

            axis=1

        )


        b=-(

            xy[:,0]**2

            +

            xy[:,1]**2

        )



        solution,_,_,_=np.linalg.lstsq(

            A,

            b,

            rcond=None

        )


        a,b_coef,c=solution



        center_xy=np.array(

            [

                -a/2,

                -b_coef/2

            ]

        )



        radius=np.sqrt(

            center_xy.dot(
                center_xy
            )

            -

            c

        )



        center=np.array(

            [

                center_xy[0],

                center_xy[1],

                np.mean(
                    P[:,2]
                )

            ]

        )



        return {

            "center":
                center,


            "radius":
                radius

        }