import numpy as np



class StructuralPrototype:


    def __init__(self):

        self.id = None

        self.primitive = []

        self.geometry = {}

        self.relations = []

        self.energy = None


        self.count = 0

        self.confidence = 0.0



    def update(self,obj):


        self.count += 1


        self.primitive = obj.get(
            "primitive",
            []
        )


        self.geometry.update({

            "center":
            np.array(
                obj["center"]
            )

        })


        self.energy=obj.get(
            "energy",
            0
        )


        self.confidence = min(

            1.0,

            self.count / 10.0

        )




    def similarity(self,obj):


        score=0.0


        primitive=obj.get(
            "primitive",
            []
        )


        if primitive in self.primitive:

            score+=0.5



        center=np.array(
            obj["center"]
        )


        if "center" in self.geometry:


            d=np.linalg.norm(

                center-

                self.geometry["center"]

            )


            score+=np.exp(
                -d
            )*0.5



        return score