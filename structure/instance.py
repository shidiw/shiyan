import hashlib
import pickle
import numpy as np


# ============================================================
# Struct3D v2.7
# Structural Instance
#
# Unit
#   ↓
# Object
#   ↓
# Instance
#
# An Instance is a concrete structural occurrence composed
# of one or more StructuralObjects.
#
# Important:
#   - geometry coordinates are NOT used for identity
#   - object ordering is canonicalized
#   - part ordering is canonicalized
#   - primitive type is preserved
#   - structural counts are preserved
#   - energy is preserved
#
# CPU only
# ============================================================


class StructuralInstance:

    def __init__(
        self,
        instance_id,
        objects
    ):

        self.id = int(instance_id)

        self.objects = (
            list(objects)
            if objects is not None
            else []
        )

        self.parts = []

        self.points = []

        self.primitives = []

        self.centers = []

        self.center = np.zeros(
            3,
            dtype=float
        )

        self.energy = 0.0

        self.num_objects = 0

        self.num_parts = 0

        self.num_points = 0

        self.signature = None

        self.hash = None

        self._collect()

        self._build_identity()


    # ========================================================
    # Generic attribute / property / method access
    # ========================================================

    @staticmethod
    def _get_value(
        obj,
        name,
        default=None
    ):

        if obj is None:

            return default

        if isinstance(
            obj,
            dict
        ):

            return obj.get(
                name,
                default
            )

        if not hasattr(
            obj,
            name
        ):

            return default

        value = getattr(
            obj,
            name
        )

        if callable(value):

            try:

                value = value()

            except TypeError:

                return default

        return value


    # ========================================================
    # Collection
    # ========================================================

    def _collect(self):

        self.parts = []

        self.points = []

        self.primitives = []

        self.centers = []

        self.energy = 0.0

        self.num_objects = len(
            self.objects
        )

        # ----------------------------------------------------
        # Traverse objects
        # ----------------------------------------------------

        for obj in self.objects:

            # ================================================
            # Object center
            # ================================================

            center = self._get_value(
                obj,
                "center",
                None
            )

            if center is not None:

                try:

                    center = np.asarray(
                        center,
                        dtype=float
                    ).reshape(-1)

                    if center.size >= 3:

                        self.centers.append(
                            center[:3]
                        )

                except Exception:

                    pass


            # ================================================
            # Object energy
            # ================================================

            energy = self._get_value(
                obj,
                "energy",
                0.0
            )

            try:

                if isinstance(
                    energy,
                    dict
                ):

                    energy = energy.get(
                        "value",
                        0.0
                    )

                self.energy += float(
                    energy
                )

            except Exception:

                pass


            # ================================================
            # Parts
            # ================================================

            parts = self._get_value(
                obj,
                "parts",
                []
            )

            if parts is None:

                parts = []


            for part in parts:

                self.parts.append(
                    part
                )


                # --------------------------------------------
                # primitive
                # --------------------------------------------

                primitive = self._get_value(
                    part,
                    "primitive",
                    "unknown"
                )

                self.primitives.append(
                    str(
                        primitive
                    )
                )


                # --------------------------------------------
                # points
                # --------------------------------------------

                points = self._get_value(
                    part,
                    "points",
                    None
                )

                if points is not None:

                    try:

                        points_array = np.asarray(
                            points
                        )

                        if (
                            points_array.ndim == 2
                            and
                            points_array.shape[1] >= 3
                        ):

                            self.points.extend(
                                points_array[:, :3]
                            )

                    except Exception:

                        pass


        # ----------------------------------------------------
        # Statistics
        # ----------------------------------------------------

        self.num_parts = len(
            self.parts
        )

        self.num_points = len(
            self.points
        )


        # ----------------------------------------------------
        # Instance center
        #
        # IMPORTANT:
        # This is geometric metadata only.
        # It is NOT part of identity.
        # ----------------------------------------------------

        if len(
            self.centers
        ) > 0:

            self.center = np.mean(
                np.asarray(
                    self.centers,
                    dtype=float
                ),
                axis=0
            )

        elif self.num_points > 0:

            self.center = np.mean(
                np.asarray(
                    self.points,
                    dtype=float
                ),
                axis=0
            )

        else:

            self.center = np.zeros(
                3,
                dtype=float
            )


    # ========================================================
    # Canonical Object Signature
    # ========================================================

    @classmethod
    def _object_signature(
        cls,
        obj
    ):

        parts = cls._get_value(
            obj,
            "parts",
            []
        )

        if parts is None:

            parts = []


        part_signatures = []


        for part in parts:

            primitive = cls._get_value(
                part,
                "primitive",
                "unknown"
            )

            primitive = str(
                primitive
            )


            points = cls._get_value(
                part,
                "points",
                []
            )

            try:

                point_count = len(
                    points
                )

            except Exception:

                point_count = 0


            energy = cls._get_value(
                part,
                "energy",
                0.0
            )

            try:

                if isinstance(
                    energy,
                    dict
                ):

                    energy = energy.get(
                        "value",
                        0.0
                    )

                energy = round(
                    float(energy),
                    8
                )

            except Exception:

                energy = 0.0


            part_signatures.append(
                (
                    primitive,
                    int(point_count),
                    energy
                )
            )


        # ----------------------------------------------------
        # Part order must NOT define identity.
        # ----------------------------------------------------

        part_signatures.sort(
            key=lambda x: (
                x[0],
                x[1],
                x[2]
            )
        )


        object_type = str(
            cls._get_value(
                obj,
                "type",
                "unknown"
            )
        )


        # ----------------------------------------------------
        # Object relation count
        #
        # Relations themselves are structural metadata.
        # Their geometric coordinates are intentionally ignored.
        # ----------------------------------------------------

        relations = cls._get_value(
            obj,
            "relations",
            []
        )

        if relations is None:

            relations = []


        relation_types = []

        for relation in relations:

            if isinstance(
                relation,
                dict
            ):

                relation_type = relation.get(
                    "type",
                    relation.get(
                        "relation",
                        "unknown"
                    )
                )

            else:

                relation_type = "unknown"

            relation_types.append(
                str(
                    relation_type
                )
            )


        relation_types.sort()


        return {

            "type":
                object_type,

            "parts":
                tuple(
                    part_signatures
                ),

            "relations":
                tuple(
                    relation_types
                )
        }


    # ========================================================
    # Canonical Instance Identity
    # ========================================================

    def _build_identity(self):

        object_signatures = []


        for obj in self.objects:

            signature = self._object_signature(
                obj
            )

            object_signatures.append(
                signature
            )


        # ----------------------------------------------------
        # Object ordering must NOT define identity.
        # ----------------------------------------------------

        object_signatures.sort(
            key=lambda x: pickle.dumps(
                x,
                protocol=4
            )
        )


        self.signature = {

            "instance_type":
                "structural_instance",

            "num_objects":
                int(
                    self.num_objects
                ),

            "num_parts":
                int(
                    self.num_parts
                ),

            "num_points":
                int(
                    self.num_points
                ),

            "objects":
                tuple(
                    object_signatures
                )
        }


        payload = pickle.dumps(
            self.signature,
            protocol=4
        )


        self.hash = hashlib.sha256(
            payload
        ).hexdigest()


    # ========================================================
    # Canonical Signature
    # ========================================================

    def canonical_signature(self):

        return self.signature


    # ========================================================
    # Identity Hash
    # ========================================================

    def identity_hash(self):

        return self.hash


    # ========================================================
    # Information
    # ========================================================

    def info(self):

        return {

            "id":
                self.id,

            "objects":
                self.num_objects,

            "parts":
                self.num_parts,

            "points":
                self.num_points,

            "primitives":
                list(
                    self.primitives
                ),

            "center":
                self.center.copy(),

            "energy":
                self.energy,

            "hash":
                self.hash
        }


    # ========================================================
    # Display
    # ========================================================

    def show(self):

        print(
            "\nStructural Instance"
        )

        print(
            "ID:",
            self.id
        )

        print(
            "Objects:",
            self.num_objects
        )

        print(
            "Parts:",
            self.num_parts
        )

        print(
            "Points:",
            self.num_points
        )

        print(
            "Primitives:",
            self.primitives
        )

        print(
            "Center:",
            self.center
        )

        print(
            "Energy:",
            self.energy
        )

        print(
            "Hash:",
            self.hash
        )


# ============================================================
# Instance Builder
# ============================================================


class StructuralInstanceBuilder:


    def build(
        self,
        units,
        objects
    ):

        # ----------------------------------------------------
        # units are retained for API compatibility.
        #
        # Instance construction is performed from objects,
        # because Object is the immediate structural parent.
        # ----------------------------------------------------

        instances = []


        if objects is None:

            objects = []


        for i, obj in enumerate(
            objects
        ):

            instance = StructuralInstance(
                instance_id=i,
                objects=[obj]
            )

            instances.append(
                instance
            )


        return instances


    # ========================================================
    # Statistics
    # ========================================================

    def statistics(
        self,
        instances
    ):

        print(
            "\nStructural Instance Statistics"
        )

        print(
            "Instances:",
            len(
                instances
            )
        )


        for instance in instances:

            print(
                "Instance",
                instance.id,
                "Objects:",
                instance.num_objects,
                "Parts:",
                instance.num_parts,
                "Points:",
                instance.num_points,
                "Primitives:",
                instance.primitives
            )


# ============================================================
# Compatibility
# ============================================================

__all__ = [

    "StructuralInstance",

    "StructuralInstanceBuilder"

]
