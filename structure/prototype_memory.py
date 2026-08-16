import os
import pickle
import numpy as np


class StructuralPrototypeMemory:
    """
    Struct3D v1.8

    Structural Prototype Memory
    ============================

    Object
        |
        v
    Structural Embedding
        |
        v
    Prototype Memory
        |
        +---- match existing prototype
        |
        +---- update prototype
        |
        +---- birth new prototype
        |
        v
    Prototype Consolidation

    Core idea
    ---------
    A prototype represents a recurring structural pattern.

    Each prototype contains:

        embedding
        primitive
        primitive_hist
        count
        age
        confidence
        stability

    Prototype evolution:

        p_{t+1}
        =
        (n_t p_t + e_{t+1}) / (n_t + 1)

    where:

        p_t       = current prototype
        e_{t+1}   = new structural embedding
        n_t       = number of observations
    """


    # =========================================================
    # Initialization
    # =========================================================

    def __init__(
        self,
        threshold=0.75,
        consolidation_threshold=0.90,
        save_path="data/prototype_memory.pkl"
    ):

        # Matching threshold
        self.threshold = float(
            threshold
        )

        # Prototype consolidation threshold
        self.consolidation_threshold = float(
            consolidation_threshold
        )

        # Persistent storage path
        self.save_path = save_path

        # Prototype database
        self.prototypes = []

        # Prototype ID generator
        self.next_id = 0


    # =========================================================
    # Threshold
    # =========================================================

    def get_threshold(
        self
    ):

        return self.threshold


    # =========================================================
    # Cosine Similarity
    # =========================================================

    def cosine(
        self,
        a,
        b
    ):

        a = np.asarray(
            a,
            dtype=np.float32
        )

        b = np.asarray(
            b,
            dtype=np.float32
        )


        # Flatten embeddings
        a = a.reshape(-1)
        b = b.reshape(-1)


        # Different dimensions cannot match
        if a.shape != b.shape:

            return 0.0


        na = np.linalg.norm(a)
        nb = np.linalg.norm(b)


        if na <= 1e-12 or nb <= 1e-12:

            return 0.0


        return float(
            np.dot(a, b)
            /
            (na * nb)
        )


    # =========================================================
    # Find Prototype
    # =========================================================

    def match(
        self,
        embedding
    ):

        if len(self.prototypes) == 0:

            return None, 0.0


        best = None
        best_score = -1.0


        for prototype in self.prototypes:

            score = self.cosine(
                embedding,
                prototype["embedding"]
            )


            if score > best_score:

                best_score = score
                best = prototype


        if best_score >= self.threshold:

            return best, best_score


        return None, best_score


    # =========================================================
    # Birth New Prototype
    # =========================================================

    def birth(
        self,
        embedding,
        primitive
    ):

        embedding = np.asarray(
            embedding,
            dtype=np.float32
        ).reshape(-1)


        proto = {

            "id":
            self.next_id,

            "primitive":
            primitive,

            "primitive_hist":
            {
                primitive: 1
            },

            "embedding":
            embedding.copy(),

            "count":
            1,

            "age":
            1,

            "confidence":
            0.1,

            "stability":
            1.0

        }


        self.next_id += 1


        self.prototypes.append(
            proto
        )


        return proto


    # =========================================================
    # Update Existing Prototype
    # =========================================================

    def update(
        self,
        prototype,
        embedding,
        primitive
    ):

        embedding = np.asarray(
            embedding,
            dtype=np.float32
        ).reshape(-1)


        count = prototype["count"]


        # -----------------------------------------------------
        # Moving average
        # -----------------------------------------------------

        prototype["embedding"] = (

            prototype["embedding"] * count
            +
            embedding

        ) / (count + 1)


        prototype["embedding"] = np.asarray(
            prototype["embedding"],
            dtype=np.float32
        )


        # -----------------------------------------------------
        # Observation statistics
        # -----------------------------------------------------

        prototype["count"] += 1

        prototype["age"] += 1


        # -----------------------------------------------------
        # Primitive statistics
        # -----------------------------------------------------

        if primitive not in prototype["primitive_hist"]:

            prototype["primitive_hist"][primitive] = 0


        prototype["primitive_hist"][primitive] += 1


        # -----------------------------------------------------
        # Dominant primitive
        # -----------------------------------------------------

        prototype["primitive"] = max(

            prototype["primitive_hist"],

            key=prototype["primitive_hist"].get

        )


        # -----------------------------------------------------
        # Confidence
        # -----------------------------------------------------

        prototype["confidence"] = (

            1.0
            -
            np.exp(
                -prototype["count"] / 10.0
            )

        )


        return prototype


    # =========================================================
    # Process One Object
    # =========================================================

    def process(
        self,
        embedding,
        primitive
    ):

        embedding = np.asarray(
            embedding,
            dtype=np.float32
        ).reshape(-1)


        prototype, score = self.match(
            embedding
        )


        # -----------------------------------------------------
        # Existing prototype
        # -----------------------------------------------------

        if prototype is not None:

            self.update(

                prototype,

                embedding,

                primitive

            )


            return {

                "status":
                "matched",

                "prototype":
                prototype,

                "score":
                score

            }


        # -----------------------------------------------------
        # New prototype
        # -----------------------------------------------------

        prototype = self.birth(

            embedding,

            primitive

        )


        return {

            "status":
            "new",

            "prototype":
            prototype,

            "score":
            score

        }


    # =========================================================
    # Process Multiple Objects
    # =========================================================

    def process_objects(
        self,
        embeddings,
        primitives
    ):

        results = []


        embeddings = np.asarray(
            embeddings,
            dtype=np.float32
        )


        if len(embeddings) != len(primitives):

            raise ValueError(
                "embeddings and primitives must have "
                "the same length"
            )


        for embedding, primitive in zip(
            embeddings,
            primitives
        ):

            result = self.process(

                embedding,

                primitive

            )


            results.append(
                result
            )


        return results


    # =========================================================
    # Evolution
    # =========================================================

    def evolve(
        self
    ):

        for prototype in self.prototypes:

            count = prototype["count"]


            # Confidence increases with observations

            prototype["confidence"] = (

                1.0
                -
                np.exp(
                    -count / 10.0
                )

            )


            # Stability depends on both confidence
            # and prototype age

            age_factor = (

                1.0
                -
                np.exp(
                    -prototype["age"] / 20.0
                )

            )


            prototype["stability"] = min(

                1.0,

                prototype["confidence"]
                *
                age_factor

            )


            # Update dominant primitive

            if len(
                prototype["primitive_hist"]
            ) > 0:

                prototype["primitive"] = max(

                    prototype["primitive_hist"],

                    key=prototype["primitive_hist"].get

                )


        return self.prototypes


    # =========================================================
    # Prototype Consolidation
    # =========================================================

    def consolidate(
        self,
        merge_threshold=None
    ):

        if merge_threshold is None:

            merge_threshold = (
                self.consolidation_threshold
            )


        merge_threshold = float(
            merge_threshold
        )


        if len(self.prototypes) <= 1:

            return self.prototypes


        merged = []

        used = set()


        for i, p1 in enumerate(
            self.prototypes
        ):

            if i in used:

                continue


            group = [p1]


            for j in range(
                i + 1,
                len(self.prototypes)
            ):

                if j in used:

                    continue


                p2 = self.prototypes[j]


                score = self.cosine(

                    p1["embedding"],

                    p2["embedding"]

                )


                if score >= merge_threshold:

                    group.append(
                        p2
                    )

                    used.add(
                        j
                    )


            # -------------------------------------------------
            # Merge group
            # -------------------------------------------------

            if len(group) > 1:

                total_count = sum(

                    p["count"]

                    for p in group

                )


                # Weighted embedding average
                embedding = sum(

                    p["embedding"] * p["count"]

                    for p in group

                ) / max(
                    total_count,
                    1
                )


                p1["embedding"] = np.asarray(
                    embedding,
                    dtype=np.float32
                )


                p1["count"] = total_count


                p1["age"] = max(

                    p["age"]

                    for p in group

                )


                # -------------------------------------------------
                # Merge primitive statistics
                # -------------------------------------------------

                primitive_hist = {}


                for p in group:

                    for primitive, count in p[
                        "primitive_hist"
                    ].items():

                        primitive_hist[primitive] = (

                            primitive_hist.get(
                                primitive,
                                0
                            )
                            +
                            count

                        )


                p1["primitive_hist"] = (
                    primitive_hist
                )


                if len(
                    primitive_hist
                ) > 0:

                    p1["primitive"] = max(

                        primitive_hist,

                        key=primitive_hist.get

                    )


                # -------------------------------------------------
                # Recompute confidence
                # -------------------------------------------------

                p1["confidence"] = (

                    1.0
                    -
                    np.exp(
                        -p1["count"] / 10.0
                    )

                )


            merged.append(
                p1
            )


        self.prototypes = merged


        self.evolve()


        return self.prototypes


    # =========================================================
    # Statistics
    # =========================================================

    def statistics(
        self
    ):

        return {

            "prototype_number":
            len(self.prototypes),

            "next_id":
            self.next_id,

            "threshold":
            self.threshold,

            "consolidation_threshold":
            self.consolidation_threshold

        }


    # =========================================================
    # Save
    # =========================================================

    def save(
        self,
        path=None
    ):

        if path is None:

            path = self.save_path


        directory = os.path.dirname(
            path
        )


        if directory:

            os.makedirs(
                directory,
                exist_ok=True
            )


        data = {

            "prototypes":
            self.prototypes,

            "next_id":
            self.next_id,

            "threshold":
            self.threshold,

            "consolidation_threshold":
            self.consolidation_threshold

        }


        with open(
            path,
            "wb"
        ) as f:

            pickle.dump(
                data,
                f
            )


        return path


    # =========================================================
    # Load
    # =========================================================

    def load(
        self,
        path=None
    ):

        if path is None:

            path = self.save_path


        if not os.path.exists(path):

            return False


        with open(
            path,
            "rb"
        ) as f:

            data = pickle.load(
                f
            )


        self.prototypes = data.get(
            "prototypes",
            []
        )


        self.next_id = data.get(
            "next_id",
            len(self.prototypes)
        )


        self.threshold = data.get(
            "threshold",
            self.threshold
        )


        self.consolidation_threshold = data.get(
            "consolidation_threshold",
            self.consolidation_threshold
        )


        return True


    # =========================================================
    # Clear
    # =========================================================

    def clear(
        self
    ):

        self.prototypes = []

        self.next_id = 0


    # =========================================================
    # Show
    # =========================================================

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


        for prototype in self.prototypes:

            print()


            print(
                "ID:",
                prototype["id"]
            )


            print(
                "Primitive:",
                prototype["primitive"]
            )


            print(
                "Count:",
                prototype["count"]
            )


            print(
                "Age:",
                prototype["age"]
            )


            print(
                "Confidence:",
                round(
                    prototype["confidence"],
                    3
                )
            )


            print(
                "Stability:",
                round(
                    prototype["stability"],
                    3
                )
            )


            print(
                "Embedding:",
                prototype["embedding"].shape
            )