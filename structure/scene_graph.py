import numpy as np



class SceneNode:


    def __init__(
        self,
        node_id,
        obj
    ):

        self.id=node_id

        self.type=getattr(
            obj,
            "type",
            "object"
        )


        self.parts=getattr(
            obj,
            "parts",
            []
        )


        self.center=np.asarray(
            getattr(
                obj,
                "center",
                np.zeros(3)
            )
        )


        self.primitives=[]


        for p in self.parts:

            if hasattr(
                p,
                "primitive"
            ):

                self.primitives.append(
                    p.primitive
                )



    def info(self):

        return {

            "id":self.id,

            "type":self.type,

            "center":self.center,

            "primitive":self.primitives

        }




class SceneEdge:


    def __init__(
        self,
        source,
        target,
        relation,
        score=1.0
    ):

        self.source=source

        self.target=target

        self.relation=relation

        self.score=score



    def info(self):

        return {

            "source":self.source,

            "target":self.target,

            "relation":self.relation,

            "score":self.score

        }




class StructuralSceneGraph:



    def __init__(self):

        self.nodes=[]

        self.edges=[]



    # ==========================================
    # Build
    # ==========================================

    def build(
        self,
        objects,
        relations=None,
        reasoning=None
    ):


        self.nodes=[]

        self.edges=[]



        # -------------------------------
        # Nodes
        # -------------------------------

        for i,obj in enumerate(objects):


            node=SceneNode(
                i,
                obj
            )

            self.nodes.append(
                node
            )



        # -------------------------------
        # Existing relations
        # -------------------------------

        if relations:


            for r in relations:


                self.edges.append(

                    SceneEdge(

                        r["source"],

                        r["target"],

                        r["type"],

                        1.0

                    )

                )



        # -------------------------------
        # Reasoning relations
        # -------------------------------

        if reasoning:


            for r in reasoning:


                self.edges.append(

                    SceneEdge(

                        r["objects"][0],

                        r["objects"][1],

                        r["type"],

                        r.get(
                            "score",
                            1.0
                        )

                    )

                )



        # -------------------------------
        # Geometric reasoning
        # -------------------------------

        self.infer_support()

        self.infer_alignment()


        return self



    # ==========================================
    # Support relation
    # ==========================================

    def infer_support(self):


        for a in self.nodes:


            for b in self.nodes:


                if a.id>=b.id:

                    continue



                dz=abs(
                    a.center[2]
                    -
                    b.center[2]
                )


                dist=np.linalg.norm(

                    a.center[:2]
                    -
                    b.center[:2]

                )



                if dz < 0.2 and dist < 4:


                    if (
                        "plane"
                        in a.primitives
                    ):


                        self.edges.append(

                            SceneEdge(

                                a.id,

                                b.id,

                                "support",

                                0.8

                            )

                        )




    # ==========================================
    # Alignment
    # ==========================================

    def infer_alignment(self):


        for a in self.nodes:


            for b in self.nodes:


                if a.id>=b.id:

                    continue



                d=np.linalg.norm(

                    a.center-b.center

                )


                if d<6:


                    self.edges.append(

                        SceneEdge(

                            a.id,

                            b.id,

                            "aligned",

                            0.5

                        )

                    )



    # ==========================================
    # Show
    # ==========================================

    def show(self):


        print(
            "\nStructural Scene Graph"
        )


        print(
            "\nNodes:"
        )


        for n in self.nodes:

            print(
                n.info()
            )



        print(
            "\nEdges:"
        )


        for e in self.edges:

            print(
                e.info()
            )



    # ==========================================
    # Statistics
    # ==========================================

    def statistics(self):


        print(
            "\nScene Graph Statistics"
        )


        print(
            "Nodes:",
            len(self.nodes)
        )


        print(
            "Edges:",
            len(self.edges)
        )


        counter={}


        for e in self.edges:


            counter[e.relation]=counter.get(
                e.relation,
                0
            )+1



        print(
            "Relations:"
        )


        for k,v in counter.items():

            print(
                k,
                ":",
                v
            )