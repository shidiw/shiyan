import numpy as np


# ==========================================================
# Structural World Model
# ==========================================================


class StructuralWorldModel:


    def __init__(self):

        self.objects = []

        self.instances = []

        self.relations = []

        self.reasoning = []

        self.units = []



    # ======================================================
    # Add Objects
    # ======================================================

    def add_objects(
        self,
        objects
    ):


        self.objects=[]


        for i,obj in enumerate(objects):


            record={

                "id": i,


                "type":
                    getattr(
                        obj,
                        "type",
                        "unknown"
                    ),


                "parts":
                    len(
                        getattr(
                            obj,
                            "parts",
                            []
                        )
                    ),



                "points":
                    self._count_points(
                        obj
                    ),



                "center":
                    self._get_center(
                        obj
                    ),



                "primitive":
                    self._get_primitives(
                        obj
                    )

            }


            self.objects.append(
                record
            )



    # ======================================================
    # Add Instances
    # ======================================================

    def add_instances(
        self,
        instances
    ):


        self.instances=[]



        for i,inst in enumerate(instances):


            # -----------------------------
            # object id
            # -----------------------------

            obj_id=i


            if hasattr(
                inst,
                "object"
            ):


                obj=getattr(
                    inst,
                    "object"
                )


                if hasattr(
                    obj,
                    "id"
                ):

                    obj_id=obj.id



            record={


                "id":
                    i,


                "object":
                    obj_id,



                "points":
                    self._count_points(
                        inst
                    ),



                "primitive":
                    self._get_primitives(
                        inst
                    ),



                "center":
                    self._get_center(
                        inst
                    )

            }



            self.instances.append(
                record
            )




    # ======================================================
    # Add Relations
    # ======================================================

    def add_relations(
        self,
        relations
    ):


        self.relations=[]


        for r in relations:


            if isinstance(
                r,
                dict
            ):


                self.relations.append(
                    r
                )


            else:


                self.relations.append(

                    {

                        "source":
                            getattr(
                                r,
                                "source",
                                None
                            ),


                        "target":
                            getattr(
                                r,
                                "target",
                                None
                            ),


                        "type":
                            getattr(
                                r,
                                "type",
                                "unknown"
                            ),


                        "distance":
                            getattr(
                                r,
                                "distance",
                                None
                            )

                    }

                )




    # ======================================================
    # Add Reasoning
    # ======================================================

    def add_reasoning(
        self,
        reasoning
    ):


        self.reasoning=[]


        for r in reasoning:


            self.reasoning.append(
                r
            )




    # ======================================================
    # Add Units
    # ======================================================

    def add_units(
        self,
        units
    ):


        self.units=units




    # ======================================================
    # Utilities
    # ======================================================


    def _count_points(
        self,
        obj
    ):


        total=0



        if hasattr(
            obj,
            "points"
        ):


            pts=obj.points


            if pts is not None:


                try:

                    total += len(
                        pts
                    )

                except:

                    pass




        if hasattr(
            obj,
            "parts"
        ):


            for p in obj.parts:


                total += self._count_points(
                    p
                )



        return total





    def _get_center(
        self,
        obj
    ):


        if hasattr(
            obj,
            "center"
        ):


            c=obj.center



            if callable(c):

                c=c()



            return np.asarray(
                c
            )



        return np.zeros(3)




    def _get_primitives(
        self,
        obj
    ):


        primitives=[]



        if hasattr(
            obj,
            "primitive"
        ):


            p=obj.primitive


            if p is not None:

                primitives.append(
                    p
                )




        if hasattr(
            obj,
            "primitives"
        ):


            primitives.extend(
                obj.primitives
            )




        if hasattr(
            obj,
            "parts"
        ):


            for part in obj.parts:


                primitives.extend(
                    self._get_primitives(
                        part
                    )
                )



        return list(
            set(
                primitives
            )
        )




    # ======================================================
    # Show
    # ======================================================


    def show(self):


        print(
            "\nStructural World Model"
        )



        print(
            "\nObjects"
        )



        for obj in self.objects:


            print(
                "Object",
                obj["id"]
            )


            print(
                " Type:",
                obj["type"]
            )


            print(
                " Parts:",
                obj["parts"]
            )


            print(
                " Points:",
                obj["points"]
            )


            print(
                " Center:",
                obj["center"]
            )


            print(
                " Primitive:",
                obj["primitive"]
            )




        print(
            "\nInstances"
        )


        for inst in self.instances:


            print(
                "Instance",
                inst["id"]
            )


            print(
                " Object:",
                inst["object"]
            )


            print(
                " Points:",
                inst["points"]
            )


            print(
                " Primitive:",
                inst["primitive"]
            )


            print(
                " Center:",
                inst["center"]
            )





        print(
            "\nRelations"
        )


        for r in self.relations:

            print(
                r
            )




        print(
            "\nReasoning"
        )


        for r in self.reasoning:

            print(
                r
            )




    # ======================================================
    # Statistics
    # ======================================================


    def statistics(self):


        total_points=0


        for inst in self.instances:

            total_points += inst["points"]



        print(
            "\nWorld Model Statistics"
        )


        print(
            "Objects:",
            len(self.objects)
        )


        print(
            "Instances:",
            len(self.instances)
        )


        print(
            "Relations:",
            len(self.relations)
        )


        print(
            "Reasoning:",
            len(self.reasoning)
        )


        print(
            "Units:",
            len(self.units)
        )


        print(
            "Points:",
            total_points
        )