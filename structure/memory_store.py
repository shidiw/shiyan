import os
import pickle
import copy


class MemoryStore:
    """
    Struct3D v1.8

    Persistent Structural Memory Store

    Responsibilities
    ----------------
    1. Store persistent objects
    2. Load objects from disk
    3. Save objects to disk
    4. Add / update objects
    5. Provide simple statistics

    This class is intentionally lightweight.
    It does not perform structural reasoning.
    It is only the persistent storage layer.
    """

    def __init__(
        self,
        path="data/structural_memory.pkl"
    ):

        self.path = path

        self.data = {
            "objects": [],
            "relations": [],
            "metadata": {}
        }

        self.load()


    # =================================================
    # Load
    # =================================================

    def load(self):

        if not os.path.exists(self.path):

            return self.data


        try:

            with open(
                self.path,
                "rb"
            ) as f:

                loaded = pickle.load(f)


            if isinstance(
                loaded,
                dict
            ):

                self.data = loaded


        except Exception:

            # If old/corrupted memory exists,
            # start with a clean memory.
            self.data = {
                "objects": [],
                "relations": [],
                "metadata": {}
            }


        return self.data


    # =================================================
    # Save
    # =================================================

    def save(self):

        directory = os.path.dirname(
            self.path
        )


        if directory:

            os.makedirs(
                directory,
                exist_ok=True
            )


        with open(
            self.path,
            "wb"
        ) as f:

            pickle.dump(
                self.data,
                f
            )


        return True


    # =================================================
    # Objects
    # =================================================

    def get_objects(self):

        return self.data["objects"]


    def set_objects(
        self,
        objects
    ):

        self.data["objects"] = copy.deepcopy(
            objects
        )


        return self.data["objects"]


    def add_object(
        self,
        obj
    ):

        self.data["objects"].append(
            copy.deepcopy(obj)
        )


        return obj


    # =================================================
    # Relations
    # =================================================

    def get_relations(self):

        return self.data["relations"]


    def set_relations(
        self,
        relations
    ):

        self.data["relations"] = copy.deepcopy(
            relations
        )


        return self.data["relations"]


    def add_relation(
        self,
        relation
    ):

        self.data["relations"].append(
            copy.deepcopy(relation)
        )


        return relation


    # =================================================
    # Metadata
    # =================================================

    def get_metadata(self):

        return self.data["metadata"]


    def set_metadata(
        self,
        key,
        value
    ):

        self.data["metadata"][key] = value


        return value


    # =================================================
    # Clear
    # =================================================

    def clear(self):

        self.data = {
            "objects": [],
            "relations": [],
            "metadata": {}
        }


        return self.data


    # =================================================
    # Statistics
    # =================================================

    def statistics(self):

        return {

            "objects":
            len(
                self.data["objects"]
            ),

            "relations":
            len(
                self.data["relations"]
            ),

            "metadata":
            len(
                self.data["metadata"]
            )

        }


    # =================================================
    # Show
    # =================================================

    def show(self):

        stats = self.statistics()


        print(
            "\nMemory Store"
        )


        print(
            "Objects:",
            stats["objects"]
        )


        print(
            "Relations:",
            stats["relations"]
        )


        print(
            "Metadata:",
            stats["metadata"]
        )


    # =================================================
    # Representation
    # =================================================

    def __len__(self):

        return len(
            self.data["objects"]
        )