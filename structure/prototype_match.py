import numpy as np



class PrototypeMatcher:


    def __init__(
        self,
        threshold=0.75
    ):

        self.threshold=threshold



    def similarity(
        self,
        a,
        b
    ):


        if not isinstance(a,dict):

            return 0.0


        if not isinstance(b,dict):

            return 0.0



        score=0.0



        pa=a.get(
            "primitive"
        )


        pb=b.get(
            "primitive"
        )



        if isinstance(pa,list):

            pa=pa[0]


        if isinstance(pb,list):

            pb=pb[0]



        if pa==pb:

            score+=0.5




        if (
            a.get("center") is not None
            and
            b.get("center") is not None
        ):


            ca=np.asarray(
                a["center"]
            )

            cb=np.asarray(
                b["center"]
            )


            d=np.linalg.norm(
                ca-cb
            )


            score+=0.3*np.exp(
                -d
            )




        ea=a.get(
            "energy",
            0
        )


        eb=b.get(
            "energy",
            0
        )


        score+=0.2*np.exp(
            -abs(ea-eb)
        )


        return score





    def find_best(
        self,
        obj,
        prototypes
    ):


        best=None

        best_score=0.0



        for p in prototypes:


            s=self.similarity(

                obj,

                p

            )


            if s>best_score:


                best_score=s

                best=p



        if best_score>=self.threshold:

            return best



        return None