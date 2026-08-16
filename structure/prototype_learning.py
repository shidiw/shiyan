import numpy as np


class PrototypeLearner:


    def __init__(self,alpha=0.1):

        self.alpha=alpha



    def update(
        self,
        prototype,
        embedding
    ):


        prototype["embedding"]=(
            (1-self.alpha)
            *
            prototype["embedding"]
            +
            self.alpha
            *
            embedding
        )


        prototype["count"]+=1



    def create(
        self,
        embedding
    ):


        return {

            "embedding":
            embedding.copy(),

            "count":
            1,

            "confidence":
            0.1

        }




    def similarity(
        self,
        a,
        b
    ):


        return np.dot(
            a,
            b
        )/(
            np.linalg.norm(a)
            *
            np.linalg.norm(b)
            +
            1e-8
        )