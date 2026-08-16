import numpy as np


class StructuralCognition:


    def __init__(self):

        self.result={}



    # -------------------------------------------------
    # Main
    # -------------------------------------------------

    def analyze(
        self,
        world,
        scene_graph,
        memory,
        reasoning
    ):


        objects = getattr(
            world,
            "objects",
            []
        )


        relations = getattr(
            scene_graph,
            "edges",
            []
        )


        self.result={

            "objects":
                len(objects),

            "relations":
                len(relations),

            "structure":
                [],

            "object_roles":
                {},

            "scene_type":
                "unknown",

            "confidence":
                0.0

        }


        self._analyze_objects(
            objects
        )


        self._analyze_relations(
            relations
        )


        self._infer_scene()



        return self.result



    # -------------------------------------------------
    # Object Understanding
    # -------------------------------------------------

    def _analyze_objects(
        self,
        objects
    ):


        roles={}


        for i,obj in enumerate(objects):


            primitive = self._primitive(
                obj
            )


            if primitive=="plane":

                roles[i]="support_surface"


            elif primitive=="sphere":

                roles[i]="object"


            else:

                roles[i]="unknown"



        self.result[
            "object_roles"
        ]=roles




    # -------------------------------------------------
    # Relation Analysis
    # -------------------------------------------------

    def _analyze_relations(
        self,
        relations
    ):


        structure=[]


        for r in relations:


            relation = self._get(
                r,
                "relation"
            )


            if relation=="support":


                structure.append(
                    {
                    "type":
                    "support_relation",

                    "base":
                    self._get(r,"source"),

                    "object":
                    self._get(r,"target"),

                    }
                )


            elif relation=="symmetry":


                structure.append(
                    {
                    "type":
                    "symmetry_pair",

                    "objects":
                    [
                    self._get(r,"source"),
                    self._get(r,"target")
                    ]

                    }
                )



        self.result[
            "structure"
        ]=structure




    # -------------------------------------------------
    # Scene Reasoning
    # -------------------------------------------------

    def _infer_scene(
        self
    ):


        roles=self.result[
            "object_roles"
        ]


        structure=self.result[
            "structure"
        ]


        has_support=False

        has_symmetry=False



        for s in structure:


            if s["type"]=="support_relation":

                has_support=True


            if s["type"]=="symmetry_pair":

                has_symmetry=True




        if has_support and has_symmetry:


            self.result[
                "scene_type"
            ]="symmetric_objects_on_surface"


            self.result[
                "confidence"
            ]=0.9



        elif has_support:


            self.result[
                "scene_type"
            ]="objects_on_surface"


            self.result[
                "confidence"
            ]=0.7



        elif has_symmetry:


            self.result[
                "scene_type"
            ]="symmetric_objects"


            self.result[
                "confidence"
            ]=0.7




    # -------------------------------------------------
    # Utils
    # -------------------------------------------------

    def _primitive(
        self,
        obj
    ):


        if hasattr(obj,"primitive"):

            p=obj.primitive

        elif isinstance(obj,dict):

            p=obj.get(
                "primitive",
                []
            )

        else:

            return None



        if isinstance(p,list):

            if len(p)>0:

                return p[0]

        return p



    def _get(
        self,
        obj,
        key
    ):


        if isinstance(obj,dict):

            return obj.get(
                key
            )


        return getattr(
            obj,
            key,
            None
        )




    # -------------------------------------------------
    # Display
    # -------------------------------------------------

    def show(
        self,
        result=None
    ):


        if result is None:

            result=self.result



        print(
            "\nStructural Cognition"
        )


        for k,v in result.items():

            print(
                k,
                ":",
                v
            )