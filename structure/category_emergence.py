import numpy as np



class StructuralCategoryEmergence:
    """
    Structural Category Emergence v2.2


    Concept
        |
        |
        v

    Category


    Robust version:
        primitive optional

        embedding mandatory
    """



    def __init__(
        self,
        threshold=0.75,
        primitive_weight=0.3,
        embedding_weight=0.7
    ):

        self.threshold = threshold

        self.primitive_weight = primitive_weight

        self.embedding_weight = embedding_weight



    # =====================================================
    # cosine
    # =====================================================

    def cosine_similarity(
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


        return np.dot(a,b)/(na*nb)



    # =====================================================
    # primitive similarity
    # =====================================================

    def primitive_similarity(
        self,
        c1,
        c2
    ):


        if (
            "primitive" not in c1
            or
            "primitive" not in c2
        ):

            return 0.0



        p1=c1["primitive"]

        p2=c2["primitive"]



        if isinstance(p1,list):

            p1=p1[0]


        if isinstance(p2,list):

            p2=p2[0]



        return 1.0 if p1==p2 else 0.0





    # =====================================================
    # Concept similarity
    # =====================================================

    def concept_similarity(
        self,
        c1,
        c2
    ):


        score=0.0


        weight=0.0



        # primitive

        ps=self.primitive_similarity(
            c1,
            c2
        )


        if ps>0:

            score += (
                self.primitive_weight
                *
                ps
            )

            weight += self.primitive_weight





        # embedding

        if (
            "embedding" in c1
            and
            "embedding" in c2
        ):


            es=self.cosine_similarity(

                c1["embedding"],

                c2["embedding"]

            )


            score += (
                self.embedding_weight
                *
                es
            )


            weight += self.embedding_weight





        if weight==0:

            return 0.0



        return score / weight







    # =====================================================
    # Build
    # =====================================================


    def build(
        self,
        concepts
    ):


        categories=[]


        visited=set()


        cid=0




        for i,c in enumerate(concepts):


            if i in visited:

                continue



            members=[i]


            visited.add(i)



            for j in range(
                i+1,
                len(concepts)
            ):


                if j in visited:

                    continue



                sim=self.concept_similarity(

                    c,

                    concepts[j]

                )



                print(
                    "Category Similarity",
                    i,
                    j,
                    sim
                )



                if sim>=self.threshold:


                    members.append(j)

                    visited.add(j)




            category=self.create_category(

                cid,

                members,

                concepts

            )


            categories.append(category)


            cid+=1




        return categories







    # =====================================================
    # Create category
    # =====================================================


    def create_category(
        self,
        cid,
        members,
        concepts
    ):


        primitives=[]

        embeddings=[]

        instances=[]


        for idx in members:


            c = concepts[idx]


            primitive = c.get(
                "primitive",
                c.get(
                    "prototype",
                    {}
                ).get(
                    "primitive",
                    None
                )
            )


            if primitive is not None:

                if isinstance(
                    primitive,
                    list
                ):
                    primitives.extend(
                        primitive
                    )

                else:

                    primitives.append(
                        primitive
                    )



            if "embedding" in c:

                embeddings.append(
                    c["embedding"]
                )


            if "instances" in c:

                instances.extend(
                    c["instances"]
                )




        if len(embeddings)>0:


            prototype=np.mean(

                np.asarray(
                    embeddings
                ),

                axis=0

            )

        else:

            prototype=None




        name=self.infer_name(

            primitives

        )




        return {


            "id":cid,


            "name":name,


            "concepts":members,


            "instances":instances,


            "primitive":
            list(set(primitives)),


            "prototype":
            prototype,


            "count":
            len(instances)

        }









    # =====================================================
    # Naming
    # =====================================================


    def infer_name(
        self,
        primitives
    ):


        if len(primitives)==0:

            return "unknown_structure"



        primitives=list(set(primitives))


        if len(primitives)==1:


            p=primitives[0]


            if p=="plane":

                return "planar_surface"



            if p=="sphere":

                return "spherical_object"



            if p=="cylinder":

                return "cylindrical_object"



            return p+"_structure"



        return "mixed_structure"








    # =====================================================
    # Show
    # =====================================================


    def show(
        self,
        categories
    ):


        print(
            "\nStructural Categories"
        )



        for c in categories:


            print()


            print(
                "Category",
                c["id"]
            )


            print(
                "Name:",
                c["name"]
            )


            print(
                "Concepts:",
                c["concepts"]
            )


            print(
                "Instances:",
                c["instances"]
            )


            print(
                "Primitive:",
                c["primitive"]
            )


            print(
                "Count:",
                c["count"]
            )