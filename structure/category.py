# ============================================================
# Struct3D v1.5
# structure/category.py
#
# Structural Category Emergence
#
# Prototype
#      |
#      v
# Category
#
# CPU only
# NumPy only
#
# ============================================================


import numpy as np



# ============================================================
# Category Emergence
# ============================================================


class StructuralCategoryEmergence:



    def __init__(
        self
    ):


        self.categories=[]



    # ========================================================
    # primitive name
    # ========================================================


    def infer_name(
        self,
        prototype
    ):


        primitive = prototype.get(
            "primitive",
            "unknown"
        )



        if isinstance(
            primitive,
            list
        ):


            if len(primitive)>0:

                primitive=primitive[0]

            else:

                primitive="unknown"



        # ----------------------------
        # structural semantics
        # ----------------------------


        if primitive=="plane":


            return "planar_surface"



        if primitive=="sphere":


            return "spherical_object"



        if primitive=="cylinder":


            return "cylindrical_object"



        if primitive=="line":


            return "linear_structure"



        return "unknown_structure"





    # ========================================================
    # feature extraction
    # ========================================================


    def feature(
        self,
        prototype
    ):


        feature=[]


        # primitive


        name=self.infer_name(
            prototype
        )


        feature.append(
            name
        )



        # energy


        energy=float(

            prototype.get(
                "energy",
                0.0
            )

        )


        feature.append(
            energy
        )



        # center


        center=np.asarray(

            prototype.get(
                "center",
                np.zeros(3)
            ),

            dtype=float

        )


        if center.size>=3:


            feature.extend(
                center[:3]
            )


        else:


            feature.extend(
                [
                    0,
                    0,
                    0
                ]
            )


        return feature





    # ========================================================
    # build
    # ========================================================


    def build(
        self,
        prototypes
    ):


        self.categories=[]



        if prototypes is None:


            return []



        for i,p in enumerate(
            prototypes
        ):



            name=self.infer_name(
                p
            )



            found=False



            # same semantic category


            for c in self.categories:



                if c["name"]==name:


                    c["instances"].append(
                        i
                    )


                    found=True


                    break




            if not found:


                category={


                    "id":
                    len(self.categories),



                    "name":
                    name,



                    "instances":
                    [
                        i
                    ],



                    "confidence":
                    0.1



                }


                self.categories.append(
                    category
                )




        # confidence update


        for c in self.categories:


            count=len(
                c["instances"]
            )


            c["confidence"]=min(

                1.0,

                0.1*count

            )



        return self.categories





    # ========================================================
    # show
    # ========================================================


    def show(
        self,
        categories=None
    ):


        if categories is None:


            categories=self.categories



        print(
            "\nStructural Categories"
        )



        for c in categories:



            print()


            print(

                "Category",

                c["id"]

            )


            print(

                "Name:",

                c["name"]

            )


            print(

                "Instances:",

                c["instances"]

            )


            print(

                "Confidence:",

                c["confidence"]

            )


        print(
            "\nEmergent Categories"
        )


        for c in categories:


            print(

                c["id"],

                c["instances"]

            )



# ============================================================
# Compatibility alias
# ============================================================


CategoryEmergence = StructuralCategoryEmergence