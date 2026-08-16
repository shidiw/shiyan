import numpy as np



class OpenWorldDetector:


    def __init__(self,threshold=0.8):

        self.threshold=threshold



    def detect(

        self,

        embedding,

        prototypes

    ):


        best=0


        for p in prototypes:


            d=np.linalg.norm(

                embedding-

                p.embedding

            )


            score=np.exp(-d)


            best=max(
                best,
                score
            )



        if best < self.threshold:


            return {

                "status":"unknown",

                "confidence":1-best

            }


        else:


            return {

                "status":"known",

                "confidence":best

            }