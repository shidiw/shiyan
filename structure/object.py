import numpy as np



class StructuralObject:


    """
    Structural Object


    Object =
        collection of structural parts


    """


    def __init__(

        self,

        parts

    ):


        self.parts = parts


        self.center = self.compute_center()



    def compute_center(self):


        centers=[]


        for p in self.parts:


            c=np.mean(

                p.points,

                axis=0

            )


            centers.append(c)



        if len(centers)==0:

            return np.zeros(3)



        return np.mean(

            centers,

            axis=0

        )





    def info(self):


        return {


            "parts":

            len(self.parts),


            "center":

            self.center


        }





class StructuralObjectBuilder:


    """
    Build Objects from Relation Graph


    Input:

        units

        relations


    Output:

        StructuralObject list


    """



    def __init__(

        self,

        merge_types=None

    ):


        if merge_types is None:


            merge_types=[

                "touching",

                "near"

            ]


        self.merge_types=merge_types





    # =================================================
    # Build
    # =================================================


    def build(

        self,

        units,

        relations

    ):


        n=len(units)



        parent=list(

            range(n)

        )



        def find(x):


            while parent[x]!=x:


                parent[x]=parent[parent[x]]


                x=parent[x]


            return x




        def union(a,b):


            ra=find(a)

            rb=find(b)


            if ra!=rb:


                parent[rb]=ra





        # ----------------------------
        # Relation based merging
        # ----------------------------


        for r in relations:


            if r["type"] in self.merge_types:


                union(

                    r["source"],

                    r["target"]

                )





        # ----------------------------
        # collect groups
        # ----------------------------


        groups={}



        for i in range(n):


            root=find(i)


            if root not in groups:


                groups[root]=[]



            groups[root].append(i)





        # ----------------------------
        # create objects
        # ----------------------------


        objects=[]



        for ids in groups.values():


            parts=[]


            for i in ids:


                parts.append(

                    units[i]

                )



            objects.append(

                StructuralObject(

                    parts

                )

            )



        return objects