import numpy as np


class PrototypeConsolidator:
    """
    Struct3D v1.8.2

    Prototype Consolidation

    Prototype
        |
        |
        v

    Stable Prototype


    Functions:

    1. confidence update
    2. stability estimation
    3. remove weak prototypes
    4. merge similar prototypes

    """



    def __init__(
        self,
        merge_threshold=0.9,
        min_count=2
    ):

        self.merge_threshold = merge_threshold

        self.min_count = min_count



    # =====================================
    # cosine
    # =====================================

    def cosine(
        self,
        a,
        b
    ):

        a=np.asarray(a)

        b=np.asarray(b)


        na=np.linalg.norm(a)

        nb=np.linalg.norm(b)


        if na==0 or nb==0:

            return 0.0


        return float(
            np.dot(a,b)
            /
            (na*nb)
        )



    # =====================================
    # confidence
    # =====================================

    def confidence(
        self,
        count
    ):


        return float(
            1-np.exp(-count/5.0)
        )



    # =====================================
    # update prototype
    # =====================================

    def update(
        self,
        prototypes
    ):


        for p in prototypes:


            p["confidence"] = self.confidence(
                p["count"]
            )


            p["stable"] = (
                p["count"]
                >=
                self.min_count
            )


        return prototypes



    # =====================================
    # merge
    # =====================================

    def merge(
        self,
        prototypes
    ):


        merged=[]

        used=set()


        for i,p1 in enumerate(prototypes):


            if i in used:

                continue


            group=[p1]


            for j,p2 in enumerate(prototypes):


                if j<=i or j in used:

                    continue


                sim=self.cosine(
                    p1["embedding"],
                    p2["embedding"]
                )


                if sim>=self.merge_threshold:


                    group.append(p2)

                    used.add(j)



            if len(group)>1:


                embedding=np.mean(
                    [
                        x["embedding"]
                        for x in group
                    ],
                    axis=0
                )


                new=group[0].copy()

                new["embedding"]=embedding

                new["count"]=sum(
                    x["count"]
                    for x in group
                )


                merged.append(new)


            else:

                merged.append(p1)



        return merged