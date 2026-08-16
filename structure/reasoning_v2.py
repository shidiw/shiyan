import numpy as np



class StructuralReasonerV2:
    """
    Struct3D v1.2

    Structural Reasoning Engine

    Input:
        World Model
        Relations

    Output:
        High level structural reasoning
    """



    def __init__(self):

        self.results = []



    # =====================================================
    # Utils
    # =====================================================

    @staticmethod
    def _safe_float(value, default=0.0):

        if value is None:
            return float(default)


        try:

            arr = np.asarray(value)


            if arr.size == 0:
                return float(default)


            x = float(
                arr.reshape(-1)[0]
            )


            if not np.isfinite(x):
                return float(default)


            return x


        except Exception:

            return float(default)



    @staticmethod
    def _get(obj, key, default=None):

        """
        Support:

        dict
        object attribute
        """

        if obj is None:
            return default


        if isinstance(obj, dict):

            return obj.get(
                key,
                default
            )


        return getattr(
            obj,
            key,
            default
        )



    # =====================================================
    # Main Interface
    # =====================================================

    def infer(
            self,
            world,
            relations
    ):


        self.results = []


        objects = self._get(
            world,
            "objects",
            []
        )


        if relations is None:

            relations=[]



        self._analyze_relations(
            relations
        )



        self._analyze_objects(
            objects
        )



        self._detect_symmetry(
            objects
        )



        return self.results



    # =====================================================
    # Relation Reasoning
    # =====================================================


    def _analyze_relations(
            self,
            relations
    ):


        for r in relations:


            r_type = self._get(
                r,
                "type",
                self._get(
                    r,
                    "relation",
                    None
                )
            )


            source = self._get(
                r,
                "source",
                -1
            )


            target = self._get(
                r,
                "target",
                -1
            )


            distance = self._safe_float(

                self._get(
                    r,
                    "distance",
                    0
                )

            )


            if r_type is None:
                continue



            # ------------------------------
            # support
            # ------------------------------

            if r_type in [
                "support",
                "support_structure"
            ]:


                self.results.append({

                    "type":
                    "support_structure",

                    "base":
                    source,

                    "supported":
                    target,

                    "confidence":
                    0.8

                })




            # ------------------------------
            # near
            # ------------------------------

            elif r_type=="near":


                self.results.append({

                    "type":
                    "near",

                    "objects":
                    [
                        source,
                        target
                    ],

                    "distance":
                    distance

                })





            # ------------------------------
            # separate
            # ------------------------------

            elif r_type=="separate":


                self.results.append({

                    "type":
                    "separate",

                    "objects":
                    [
                        source,
                        target
                    ],

                    "distance":
                    distance

                })





            # ------------------------------
            # aligned
            # ------------------------------

            elif r_type=="aligned":


                self.results.append({

                    "type":
                    "aligned",

                    "objects":
                    [
                        source,
                        target
                    ],

                    "confidence":
                    self._safe_float(
                        self._get(
                            r,
                            "score",
                            0.5
                        )
                    )

                })




    # =====================================================
    # Object Analysis
    # =====================================================


    def _analyze_objects(
            self,
            objects
    ):


        for idx,obj in enumerate(objects):


            primitive = self._get(
                obj,
                "primitive",
                []
            )


            if isinstance(
                primitive,
                list
            ):

                primitive_type = primitive

            else:

                primitive_type=[
                    primitive
                ]



            self.results.append({

                "type":
                "object_state",

                "object":
                idx,

                "primitive":
                primitive_type

            })





    # =====================================================
    # Symmetry
    # =====================================================


    def _detect_symmetry(
            self,
            objects
    ):


        n=len(objects)


        for i in range(n):

            for j in range(
                i+1,
                n
            ):


                pi=self._get(
                    objects[i],
                    "primitive",
                    None
                )


                pj=self._get(
                    objects[j],
                    "primitive",
                    None
                )


                if pi==pj and pi is not None:


                    self.results.append({

                        "type":
                        "symmetry",

                        "objects":
                        [
                            i,
                            j
                        ],

                        "score":
                        1.0

                    })





    # =====================================================
    # Show
    # =====================================================


    def show(
            self,
            results=None
    ):


        if results is None:

            results=self.results



        for r in results:

            print(r)