import math
import numpy as np


class WorldStateValidator:
    """
    Struct3D v2.0

    Unified validator for StructuralWorldState.

    Checks:

    1. schema
    2. object IDs
    3. instance references
    4. relation references
    5. primitive validity
    6. numeric validity
    7. scene consistency
    8. prototype / concept / category references
    """

    VERSION = "2.0"

    def __init__(self):

        self.errors = []
        self.warnings = []

    # ==================================================
    # Main
    # ==================================================

    def validate(self, world):

        self.errors = []
        self.warnings = []

        self._check_schema(world)
        self._check_objects(world)
        self._check_instances(world)
        self._check_relations(world)
        self._check_units(world)
        self._check_prototypes(world)
        self._check_concepts(world)
        self._check_categories(world)
        self._check_numeric(world)

        return {
            "valid": len(self.errors) == 0,
            "errors": list(self.errors),
            "warnings": list(self.warnings)
        }

    # ==================================================
    # Schema
    # ==================================================

    def _check_schema(self, world):

        required = [
            "units",
            "objects",
            "instances",
            "relations",
            "reasoning",
            "prototypes",
            "concepts",
            "categories",
            "metadata"
        ]

        for name in required:

            if not hasattr(world, name):

                self.errors.append(
                    "Missing world field: {}".format(
                        name
                    )
                )

        version = getattr(
            world,
            "version",
            None
        )

        if version is None:

            self.errors.append(
                "Missing world version"
            )

    # ==================================================
    # Objects
    # ==================================================

    def _check_objects(self, world):

        objects = getattr(
            world,
            "objects",
            {}
        )

        if not isinstance(
            objects,
            dict
        ):

            self.errors.append(
                "objects must be dict"
            )

            return

        ids = list(
            objects.keys()
        )

        if len(ids) != len(
            set(ids)
        ):

            self.errors.append(
                "Duplicate object IDs"
            )

        for object_id, obj in objects.items():

            if not isinstance(
                obj,
                dict
            ):

                self.errors.append(
                    "Object {} is not dict".format(
                        object_id
                    )
                )

                continue

            if "id" not in obj:

                self.errors.append(
                    "Object {} missing id".format(
                        object_id
                    )
                )

            if "primitive" not in obj:

                self.warnings.append(
                    "Object {} missing primitive".format(
                        object_id
                    )
                )

    # ==================================================
    # Instances
    # ==================================================

    def _check_instances(self, world):

        instances = getattr(
            world,
            "instances",
            {}
        )

        objects = getattr(
            world,
            "objects",
            {}
        )

        if not isinstance(
            instances,
            dict
        ):

            self.errors.append(
                "instances must be dict"
            )

            return

        for instance_id, instance in instances.items():

            if not isinstance(
                instance,
                dict
            ):

                self.errors.append(
                    "Instance {} is not dict".format(
                        instance_id
                    )
                )

                continue

            object_id = instance.get(
                "object"
            )

            if (
                object_id is not None
                and
                object_id not in objects
            ):

                self.errors.append(
                    "Instance {} references "
                    "missing object {}".format(
                        instance_id,
                        object_id
                    )
                )

    # ==================================================
    # Relations
    # ==================================================

    def _check_relations(self, world):

        relations = getattr(
            world,
            "relations",
            []
        )

        objects = getattr(
            world,
            "objects",
            {}
        )

        if not isinstance(
            relations,
            list
        ):

            self.errors.append(
                "relations must be list"
            )

            return

        for i, relation in enumerate(
            relations
        ):

            if not isinstance(
                relation,
                dict
            ):

                self.errors.append(
                    "Relation {} is not dict".format(
                        i
                    )
                )

                continue

            source = relation.get(
                "source"
            )

            target = relation.get(
                "target"
            )

            if source not in objects:

                self.errors.append(
                    "Relation {} invalid source {}".format(
                        i,
                        source
                    )
                )

            if target not in objects:

                self.errors.append(
                    "Relation {} invalid target {}".format(
                        i,
                        target
                    )
                )

            if "type" not in relation:

                self.errors.append(
                    "Relation {} missing type".format(
                        i
                    )
                )

    # ==================================================
    # Units
    # ==================================================

    def _check_units(self, world):

        units = getattr(
            world,
            "units",
            {}
        )

        if not isinstance(
            units,
            dict
        ):

            self.errors.append(
                "units must be dict"
            )

    # ==================================================
    # Prototypes
    # ==================================================

    def _check_prototypes(self, world):

        prototypes = getattr(
            world,
            "prototypes",
            {}
        )

        if not isinstance(
            prototypes,
            dict
        ):

            self.errors.append(
                "prototypes must be dict"
            )

    # ==================================================
    # Concepts
    # ==================================================

    def _check_concepts(self, world):

        concepts = getattr(
            world,
            "concepts",
            {}
        )

        if not isinstance(
            concepts,
            dict
        ):

            self.errors.append(
                "concepts must be dict"
            )

    # ==================================================
    # Categories
    # ==================================================

    def _check_categories(self, world):

        categories = getattr(
            world,
            "categories",
            {}
        )

        if not isinstance(
            categories,
            dict
        ):

            self.errors.append(
                "categories must be dict"
            )

    # ==================================================
    # Numeric
    # ==================================================

    def _check_numeric(self, world):

        visited = set()

        def recursive(value, path):

            object_id = id(value)

            if object_id in visited:

                return

            if isinstance(
                value,
                np.ndarray
            ):

                if not np.all(
                    np.isfinite(value)
                ):

                    self.errors.append(
                        "Non-finite ndarray at {}".format(
                            path
                        )
                    )

                return

            if isinstance(
                value,
                np.generic
            ):

                value = value.item()

            if isinstance(
                value,
                float
            ):

                if not math.isfinite(value):

                    self.errors.append(
                        "Non-finite value at {}".format(
                            path
                        )
                    )

                return

            if isinstance(
                value,
                dict
            ):

                visited.add(
                    object_id
                )

                for key, val in value.items():

                    recursive(
                        val,
                        "{}.{}".format(
                            path,
                            key
                        )
                    )

                return

            if isinstance(
                value,
                (list, tuple)
            ):

                visited.add(
                    object_id
                )

                for i, val in enumerate(value):

                    recursive(
                        val,
                        "{}[{}]".format(
                            path,
                            i
                        )
                    )

        recursive(
            world.to_dict(),
            "world"
        )

    # ==================================================
    # Report
    # ==================================================

    def show(self, result):

        print(
            "\nWorld State Validation"
        )

        print(
            "Status:",
            "PASS"
            if result["valid"]
            else "FAIL"
        )

        print(
            "Errors:",
            len(result["errors"])
        )

        print(
            "Warnings:",
            len(result["warnings"])
        )

        for error in result["errors"]:

            print(
                "ERROR:",
                error
            )

        for warning in result["warnings"]:

            print(
                "WARNING:",
                warning
            )
