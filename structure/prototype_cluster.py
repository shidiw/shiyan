import numpy as np



class PrototypeCluster:



    def __init__(self,threshold=0.8):

        self.threshold=threshold



    def distance(
        self,
        a,
        b
    ):


        score=0



        if a.primitive == b.primitive:

            score+=0.6



        if "center" in a.geometry and "center" in b.geometry:


            d=np.linalg.norm(

                a.geometry["center"]

                -

                b.geometry["center"]

            )


            score+=0.4*np.exp(-d)



        return score



    def cluster(self,prototypes):


        groups=[]


        used=set()



        for i,p in enumerate(prototypes):


            if i in used:

                continue



            group=[p]

            used.add(i)



            for j,q in enumerate(prototypes):


                if j in used:

                    continue



                s=self.distance(
                    p,
                    q
                )


                if s>self.threshold:

                    group.append(q)

                    used.add(j)



            groups.append(group)



        return groups