import numpy as np


class PrototypeGeneralizer:
    """
    Structural Prototype Generalization v5.0

    Object
        |
        v
    Prototype
        |
        v
    Concept

    Fusion:

    Similarity =
        w1 * Embedding Similarity
      + w2 * Primitive Similarity
      + w3 * Parameter Similarity

    """


    def __init__(
        self,
        threshold=0.55,
        embedding_weight=0.5,
        primitive_weight=0.3,
        parameter_weight=0.2
    ):

        self.threshold = threshold

        self.embedding_weight = embedding_weight

        self.primitive_weight = primitive_weight

        self.parameter_weight = parameter_weight



    # =====================================================
    # Primitive Similarity
    # =====================================================

    def primitive_similarity(
        self,
        p1,
        p2
    ):

        """
        primitive invariant

        sphere == sphere

        plane == plane

        """

        if isinstance(p1,list):
            p1=p1[0]

        if isinstance(p2,list):
            p2=p2[0]


        if p1 == p2:

            return 1.0


        return 0.0




    # =====================================================
    # Parameter Similarity
    # =====================================================

    def parameter_similarity(
        self,
        a,
        b
    ):

        """
        Compare primitive parameters.

        Not exact matching.

        Example:

        sphere:

        r=1.0
        r=1.15

        still similar.

        """


        if a is None or b is None:

            return 0.0



        values_a=[]
        values_b=[]


        for k in a:


            if k in b:


                va=a[k]
                vb=b[k]


                if np.isscalar(va):

                    values_a.append(
                        float(va)
                    )

                    values_b.append(
                        float(vb)
                    )


                else:

                    va=np.asarray(
                        va
                    )

                    vb=np.asarray(
                        vb
                    )


                    values_a.extend(
                        va.flatten()
                    )

                    values_b.extend(
                        vb.flatten()
                    )



        if len(values_a)==0:

            return 0.5



        values_a=np.asarray(
            values_a
        )

        values_b=np.asarray(
            values_b
        )


        diff=np.linalg.norm(
            values_a-values_b
        )


        scale=(
            np.linalg.norm(values_a)
            +
            np.linalg.norm(values_b)
            +
            1e-6
        )


        similarity=np.exp(
            -diff/scale
        )


        return float(
            similarity
        )





    # =====================================================
    # Embedding Similarity
    # =====================================================

    def embedding_similarity(
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
    # Total Similarity
    # =====================================================

    def similarity(
        self,
        proto_a,
        proto_b,
        emb_a,
        emb_b
    ):


        s_embedding = self.embedding_similarity(
            emb_a,
            emb_b
        )



        s_primitive = self.primitive_similarity(

            proto_a["primitive"],

            proto_b["primitive"]

        )



        s_parameter = self.parameter_similarity(

            proto_a.get(
                "parameters",
                None
            ),

            proto_b.get(
                "parameters",
                None
            )

        )



        score=(

            self.embedding_weight
            *
            s_embedding

            +

            self.primitive_weight
            *
            s_primitive

            +

            self.parameter_weight
            *
            s_parameter

        )



        return score





    # =====================================================
    # Generalization
    # =====================================================

    def generalize(
        self,
        prototypes,
        embeddings
    ):


        concepts=[]

        visited=set()



        for i in range(len(prototypes)):


            if i in visited:
                continue



            members=[i]


            visited.add(i)



            for j in range(
                i+1,
                len(prototypes)
            ):


                if j in visited:
                    continue



                score=self.similarity(

                    prototypes[i],

                    prototypes[j],

                    embeddings[i],

                    embeddings[j]

                )



                print(
                    "Prototype Similarity",
                    i,
                    j,
                    score
                )



                if score >= self.threshold:


                    members.append(j)

                    visited.add(j)



            # ==========================
            # create concept
            # ==========================


            concept_embeddings=[]

            for m in members:

                concept_embeddings.append(
                    embeddings[m]
                )



            concept_embedding=np.mean(
                np.asarray(
                    concept_embeddings
                ),
                axis=0
            )



            concept={


                "id":
                len(concepts),


                "instances":
                members,


                "prototype":
                prototypes[members[0]],


                "embedding":
                concept_embedding


            }



            concepts.append(
                concept
            )



        return concepts





    # =====================================================
    # Show
    # =====================================================

    def show(
        self,
        concepts
    ):


        print(
            "\nStructural Concepts\n"
        )


        for c in concepts:


            proto=c["prototype"]


            primitive=proto["primitive"]


            if isinstance(
                primitive,
                list
            ):

                primitive=primitive[0]



            print(
                "Concept",
                c["id"]
            )


            print(
                "Instances:",
                c["instances"]
            )


            print(
                "Primitive:",
                primitive
            )


            print(
                "Count:",
                len(c["instances"])
            )


            print(
                "Confidence:",
                round(
                    min(
                        1.0,
                        0.5
                        +
                        0.25*
                        len(c["instances"])
                    ),
                    3
                )
            )


            print()
