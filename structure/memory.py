import os
import numpy as np

from structure.memory_store import MemoryStore


class StructuralMemory:
    """
    Struct3D v1.8

    Persistent Structural Memory

    Responsibilities
    ----------------
    1. Match current objects against persistent objects
    2. Create new persistent objects
    3. Update persistent objects
    4. Preserve object identity across runs
    5. Store relations
    6. Persist memory through MemoryStore

    MemoryStore is only responsible for persistence.
    StructuralMemory is responsible for structural memory logic.
    """

    def __init__(
        self,
        threshold=0.5,
        path="data/structural_memory.pkl"
    ):

        self.threshold = threshold

        self.memory = {}

        self.next_id = 10000

        self.matches = 0

        self.new_objects = 0

        self.store = MemoryStore(
            path=path
        )

        self.load()

    # ==================================================
    # Threshold
    # ==================================================

    def get_threshold(self):

        return self.threshold

    # ==================================================
    # Object Feature
    # ==================================================

    def _primitive_signature(
        self,
        obj
    ):

        primitives = getattr(
            obj,
            "primitives",
            []
        )

        if isinstance(
            primitives,
            str
        ):

            primitives = [
                primitives
            ]

        return tuple(
            primitives
        )

    # ==================================================
    # Object Center
    # ==================================================

    def _center(
        self,
        obj
    ):

        center = getattr(
            obj,
            "center",
            None
        )

        if center is None:

            return np.zeros(
                3,
                dtype=np.float64
            )

        return np.asarray(
            center,
            dtype=np.float64
        )

    # ==================================================
    # Object Similarity
    # ==================================================

    def similarity(
        self,
        obj_a,
        obj_b
    ):

        primitive_a = self._primitive_signature(
            obj_a
        )

        primitive_b = self._primitive_signature(
            obj_b
        )

        # Primitive mismatch
        if primitive_a != primitive_b:

            return 0.0

        center_a = self._center(
            obj_a
        )

        center_b = self._center(
            obj_b
        )

        distance = np.linalg.norm(
            center_a - center_b
        )

        # Structural identity is based primarily
        # on primitive type and spatial continuity.

        score = np.exp(
            -distance
        )

        return float(
            score
        )

    # ==================================================
    # Find Match
    # ==================================================

    def match(
        self,
        obj
    ):

        if len(self.memory) == 0:

            return None

        best_id = None

        best_score = -1.0

        for object_id, stored in self.memory.items():

            score = self.similarity(
                obj,
                stored
            )

            if score > best_score:

                best_score = score

                best_id = object_id

        if best_score >= self.threshold:

            return best_id

        return None

    # ==================================================
    # Convert Object To Persistent Record
    # ==================================================

    def _record(
        self,
        object_id,
        obj,
        age=1
    ):

        return {

            "id":
            object_id,

            "primitive":
            list(
                self._primitive_signature(
                    obj
                )
            ),

            "center":
            self._center(
                obj
            ).copy(),

            "energy":
            float(
                getattr(
                    obj,
                    "energy",
                    0.0
                )
            ),

            "age":
            age
        }

    # ==================================================
    # Update Existing Object
    # ==================================================

    def _update_record(
        self,
        record,
        obj
    ):

        old_center = np.asarray(
            record["center"],
            dtype=np.float64
        )

        new_center = self._center(
            obj
        )

        age = int(
            record.get(
                "age",
                1
            )
        )

        # Exponential moving average
        alpha = 0.2

        record["center"] = (
            (1.0 - alpha) * old_center
            +
            alpha * new_center
        )

        record["energy"] = float(
            getattr(
                obj,
                "energy",
                record.get(
                    "energy",
                    0.0
                )
            )
        )

        record["age"] = age + 1

        return record

    # ==================================================
    # Update Memory
    # ==================================================

    def update(
        self,
        objects,
        relations=None
    ):

        current_ids = []

        self.matches = 0

        self.new_objects = 0

        for obj in objects:

            matched_id = self.match(
                obj
            )

            # ------------------------------------------
            # Existing object
            # ------------------------------------------

            if matched_id is not None:

                object_id = matched_id

                record = self.memory[
                    object_id
                ]

                self._update_record(
                    record,
                    obj
                )

                self.matches += 1

            # ------------------------------------------
            # New object
            # ------------------------------------------

            else:

                object_id = self.next_id

                self.next_id += 1

                self.memory[
                    object_id
                ] = self._record(
                    object_id,
                    obj,
                    age=1
                )

                self.new_objects += 1

            current_ids.append(
                object_id
            )

        # Store current relations
        if relations is not None:

            self._store_relations(
                relations
            )

        self.save()

        return current_ids

    # ==================================================
    # Relations
    # ==================================================

    def _store_relations(
        self,
        relations
    ):

        normalized = []

        for relation in relations:

            if isinstance(
                relation,
                dict
            ):

                normalized.append(
                    relation.copy()
                )

        self.store.set_relations(
            normalized
        )

    # ==================================================
    # Save
    # ==================================================

    def save(self):

        objects = list(
            self.memory.values()
        )

        self.store.set_objects(
            objects
        )

        self.store.set_metadata(
            "next_id",
            int(
                self.next_id
            )
        )

        self.store.set_metadata(
            "threshold",
            float(
                self.threshold
            )
        )

        self.store.save()

        return True

    # ==================================================
    # Load
    # ==================================================

    def load(self):

        data = self.store.load()

        objects = data.get(
            "objects",
            []
        )

        metadata = data.get(
            "metadata",
            {}
        )

        self.memory = {}

        for obj in objects:

            if not isinstance(
                obj,
                dict
            ):

                continue

            if "id" not in obj:

                continue

            try:

                object_id = int(
                    obj["id"]
                )

            except (
                TypeError,
                ValueError
            ):

                continue

            self.memory[
                object_id
            ] = obj

        # ------------------------------------------
        # Restore next ID
        # ------------------------------------------

        stored_next_id = metadata.get(
            "next_id",
            None
        )

        try:

            if stored_next_id is not None:

                self.next_id = int(
                    stored_next_id
                )

            elif len(self.memory) > 0:

                self.next_id = max(
                    int(x)
                    for x in self.memory.keys()
                ) + 1

            else:

                self.next_id = 10000

        except (
            TypeError,
            ValueError
        ):

            self.next_id = 10000

        # Never allow IDs below the Struct3D
        # persistent-object namespace.

        self.next_id = max(
            self.next_id,
            10000
        )

        return self.memory

    # ==================================================
    # Clear
    # ==================================================

    def clear(self):

        self.memory = {}

        self.next_id = 10000

        self.matches = 0

        self.new_objects = 0

        self.store.clear()

        self.save()

    # ==================================================
    # Statistics
    # ==================================================

    def statistics(self):

        result = {

            "objects":
            len(
                self.memory
            ),

            "new":
            self.new_objects,

            "matched":
            self.matches,

            "next_id":
            self.next_id,

            "threshold":
            self.threshold

        }

        print(
            "\nMemory Statistics"
        )

        print(
            "Objects:",
            result["objects"]
        )

        print(
            "New:",
            result["new"]
        )

        print(
            "Matched:",
            result["matched"]
        )

        return result

    # ==================================================
    # Show
    # ==================================================

    def show(self):

        print(
            "\nPersistent Objects"
        )

        if len(
            self.memory
        ) == 0:

            print(
                "Empty"
            )

            return

        for object_id in sorted(
            self.memory.keys()
        ):

            obj = self.memory[
                object_id
            ]

            print()

            print(
                "ID:",
                object_id
            )

            print(
                "Primitive:",
                obj.get(
                    "primitive",
                    []
                )
            )

            print(
                "Center:",
                obj.get(
                    "center",
                    None
                )
            )

            print(
                "Age:",
                obj.get(
                    "age",
                    0
                )
            )

    # ==================================================
    # Get Object
    # ==================================================

    def get(
        self,
        object_id
    ):

        return self.memory.get(
            object_id
        )

    # ==================================================
    # Get All
    # ==================================================

    def get_all(self):

        return list(
            self.memory.values()
        )