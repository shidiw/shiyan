import numpy as np


class StructuralPrototypeMemory:
    """
    Struct3D v1.8.1

    Prototype Evolution Memory


    Object
        |
        v

    Structural Embedding

        |
        v

    Prototype Memory


    match
        |
        +---- existing prototype update
        |
        +---- new prototype birth

    """


    def __init__(
        self,
        threshold=0.75
    ):

        self.threshold = threshold

        # prototype database
        self.prototypes = []

        # id generator
        self.next_id = 0



    # =====================================================
    # threshold
    # =====================================================

    def get_threshold(
        self
    ):

        return self.threshold



    # =====================================================
    # cosine similarity
    # =====================================================

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



    # =====================================================
    # Find Prototype
    # =====================================================

    def match(
        self,
        embedding
    ):


        if len(self.prototypes)==0:

            return None,0.0



        best=None

        best_score=-1.0



        for p in self.prototypes:


            score=self.cosine(

                embedding,

                p["embedding"]

            )


            if score > best_score:

                best_score=score

                best=p



        if best_score >= self.threshold:

            return best,best_score



        return None,best_score




    # =====================================================
    # Update Existing Prototype
    # =====================================================

    def update(
        self,
        prototype,
        embedding
    ):


        count=prototype["count"]



        prototype["embedding"]=(

            prototype["embedding"]*count

            +

            embedding

        )/(count+1)



        prototype["count"] += 1


        prototype["age"] += 1



        return prototype




    # =====================================================
    # Birth New Prototype
    # =====================================================

    def birth(
        self,
        embedding,
        primitive
    ):


        proto={


            "id":
            self.next_id,


            "primitive":
            primitive,


            "embedding":
            np.asarray(
                embedding,
                dtype=np.float32
            ),


            "count":
            1,


            "age":
            1

        }



        self.next_id += 1



        self.prototypes.append(
            proto
        )



        return proto




    # =====================================================
    # Process Object
    # =====================================================

    def process(
        self,
        embedding,
        primitive
    ):


        proto,score=self.match(
            embedding
        )



        # existing prototype

        if proto is not None:


            self.update(

                proto,

                embedding

            )


            return {


                "status":
                "matched",


                "prototype":
                proto,


                "score":
                score


            }



        # new prototype

        proto=self.birth(

            embedding,

            primitive

        )


        return {


            "status":
            "new",


            "prototype":
            proto,


            "score":
            score


        }




    # =====================================================
    # Statistics
    # =====================================================

    def statistics(
        self
    ):


        return {


            "prototypes":
            len(self.prototypes),


            "next_id":
            self.next_id

        }




    # =====================================================
    # Show
    # =====================================================

    def show(
        self
    ):


        print(
            "\nStructural Prototype Memory"
        )


        print(

            "Prototype Number:",

            len(self.prototypes)

        )



        for p in self.prototypes:


            print()


            print(

                "ID:",

                p["id"]

            )


            print(

                "Primitive:",

                p["primitive"]

            )


            print(

                "Count:",

                p["count"]

            )


            print(

                "Age:",

                p["age"]

            )


            print(

                "Embedding:",

                p["embedding"].shape

            )