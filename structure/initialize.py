import numpy as np

from .unit import StructuralUnit



class PrimitiveInitializer:
    """
    Primitive Initialization Module

    Geometry Field:

        curvature
        eigenvalues

        |
        v

    Structural Units:

        Plane
        Sphere
        Cylinder

    """


    def __init__(
        self,
        curvature_threshold=0.015,
        sphere_ratio_threshold=0.35
    ):

        self.curvature_threshold = (
            curvature_threshold
        )

        self.sphere_ratio_threshold = (
            sphere_ratio_threshold
        )



    def initialize(
        self,
        points,
        field
    ):
        """
        Primitive discovery

        Args:

            points:
                (N,3)

            field:
                GeometryField output

        Returns:

            StructuralUnit list

        """


        curvature = field["curvature"]

        eigenvalues = field["eigenvalues"]



        # normalize curvature

        curvature_norm = (
            curvature
            /
            (
                np.max(curvature)
                +
                1e-12
            )
        )


        labels = np.zeros(
            len(points),
            dtype=np.int32
        )



        for i in range(len(points)):


            k = curvature_norm[i]


            eig = eigenvalues[i]


            #
            # sort eigenvalues
            #
            # lambda0 <= lambda1 <= lambda2
            #

            l0,l1,l2 = eig



            #
            # Plane
            #
            # Surface variation small
            #

            if k < self.curvature_threshold:


                labels[i]=0



            else:


                #
                # Sphere
                #
                # two tangent directions similar
                #

                sphere_ratio = abs(
                    l2-l1
                ) / (
                    l2+1e-12
                )



                if (
                    sphere_ratio
                    <
                    self.sphere_ratio_threshold
                ):

                    labels[i]=1


                else:


                    #
                    # Cylinder
                    #

                    labels[i]=2




        units = self._create_units(
            points,
            labels
        )


        return units




    def _create_units(
        self,
        points,
        labels
    ):


        units=[]


        primitive_names=[

            "plane",

            "sphere",

            "cylinder"

        ]



        for pid,name in enumerate(
            primitive_names
        ):


            mask = (
                labels == pid
            )


            count=np.sum(mask)



            if count == 0:

                continue



            unit = StructuralUnit(

                points[mask],

                name,

                np.where(mask)[0]

            )



            unit.estimate_parameters()


            units.append(unit)



        return units



    def statistics(
        self,
        units
    ):

        """
        Debug statistics
        """


        print(
            "\nPrimitive Statistics"
        )


        for u in units:


            print(
                u.primitive,
                ":",
                u.size()
            )