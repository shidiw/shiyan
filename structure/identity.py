import numpy as np


class ObjectIdentity:


    def __init__(self):

        self.counter = 0



    def assign(self, objects):

        for obj in objects:

            if obj.id is None:

                obj.id = self.counter

                self.counter += 1


        return objects



class StructuralObject:


    def __init__(self,
                 parts,
                 obj_type="single"):


        self.id=None

        self.parts=parts

        self.type=obj_type

        self.center=self.compute_center()

        self.relations=[]



    def compute_center(self):

        centers=[]

        for p in self.parts:

            centers.append(
                p.center
            )


        return np.mean(
            centers,
            axis=0
        )



    def add_relation(
        self,
        relation
    ):

        self.relations.append(
            relation
        )


    def info(self):

        return {

            "id":self.id,

            "type":self.type,

            "parts":[
                p.id for p in self.parts
            ],

            "center":self.center,

            "relations":
                self.relations

        }