import numpy as np



class StructuralReasoner:


    def __init__(
        self,
        near_threshold=3.5,
        symmetry_threshold=0.8
    ):

        self.near_threshold = near_threshold

        self.symmetry_threshold = symmetry_threshold



    # ==================================================
    # distance
    # ==================================================

    def distance(
        self,
        a,
        b
    ):

        ca=np.asarray(
            a.center
        )

        cb=np.asarray(
            b.center
        )


        return np.linalg.norm(
            ca-cb
        )



    # ==================================================
    # symmetry
    # ==================================================

    def symmetry_score(
        self,
        a,
        b
    ):

        da=self.distance(
            a,
            b
        )


        if da==0:
            return 1.0


        # primitive similarity

        score=0.0


        if hasattr(a,"primitives") and hasattr(b,"primitives"):

            pa=a.primitives
            pb=b.primitives


            if len(pa)==len(pb):

                score+=0.5



        # center opposite relation

        ca=np.asarray(
            a.center
        )

        cb=np.asarray(
            b.center
        )


        mid=(ca+cb)/2


        if np.linalg.norm(mid)<0.5:

            score+=0.5



        return score



    # ==================================================
    # relation inference
    # ==================================================

    def infer(
        self,
        objects,
        relations=None
    ):


        results=[]


        n=len(objects)



        for i in range(n):


            for j in range(
                i+1,
                n
            ):


                a=objects[i]

                b=objects[j]


                d=self.distance(
                    a,
                    b
                )


                # -----------------------------
                # near
                # -----------------------------

                if d < self.near_threshold:


                    results.append(
                    {

                        "type":"near",

                        "objects":[
                            i,
                            j
                        ],

                        "distance":float(d)

                    }
                    )



                # -----------------------------
                # symmetry
                # -----------------------------


                s=self.symmetry_score(
                    a,
                    b
                )


                if s>=self.symmetry_threshold:


                    results.append(
                    {

                        "type":"symmetry",

                        "objects":[
                            i,
                            j
                        ],

                        "score":float(s)

                    }
                    )



        return results



    # ==================================================
    # display
    # ==================================================

    def show(
        self,
        reasoning
    ):


        print(
            "\nStructural Reasoning"
        )


        for r in reasoning:

            print(
                r
            )
