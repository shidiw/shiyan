import os
import sys
import traceback
import numpy as np

ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


# ============================================================
# Struct3D modules
# ============================================================

from geometry.field import GeometryField
from graph.relation import StructuralGraph

from structure.graph_cluster import GraphStructuralCluster
from structure.merge import StructuralMerger
from structure.optimize import StructuralOptimizer
from structure.primitive_selector import PrimitiveSelector
from structure.energy import StructureEnergy

from structure.hierarchy import StructuralHierarchy
from structure.relation import StructuralRelationGraph
from structure.assembly import StructuralObjectAssembly
from structure.instance import StructuralInstanceBuilder

from structure.world_state import StructuralWorldState
from structure.world_validator import WorldStateValidator

from structure.object_embedding import StructuralEmbedding
from structure.prototype_memory import StructuralPrototypeMemory
from structure.prototype_generalization import PrototypeGeneralizer
from structure.category_emergence import StructuralCategoryEmergence

from structure.reasoning_v2 import StructuralReasonerV2
from structure.cognition import StructuralCognition


# ============================================================
# Utility
# ============================================================

RESULTS = {}


def stage(name):
    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)


def success(name):
    RESULTS[name] = True
    print("[PASS]", name)


def failure(name, exc):
    RESULTS[name] = False
    print("[FAIL]", name)
    print("Error:", repr(exc))
    traceback.print_exc()


# ============================================================
# Load
# ============================================================

def load_data():

    path = os.path.join(
        ROOT,
        "data",
        "primitives.npy"
    )

    if not os.path.exists(path):
        raise FileNotFoundError(path)

    points = np.load(path)

    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError(
            "Expected N x 3 point cloud, got {}".format(
                points.shape
            )
        )

    return points


# ============================================================
# Main pipeline
# ============================================================

def run_pipeline(points):

    # --------------------------------------------------------
    # Geometry
    # --------------------------------------------------------

    field_model = GeometryField(
        points,
        k=15
    )

    field = field_model.compute()

    assert "normals" in field
    assert "curvature" in field
    assert "eigenvalues" in field

    # --------------------------------------------------------
    # Structural Graph
    # --------------------------------------------------------

    graph_model = StructuralGraph(
        k=30
    )

    graph = graph_model.build(
        points,
        field["normals"],
        field["curvature"]
    )

    # --------------------------------------------------------
    # Structural Units
    # --------------------------------------------------------

    cluster = GraphStructuralCluster(
        threshold=0.25,
        min_points=200
    )

    units = cluster.extract(
        points,
        graph
    )

    # --------------------------------------------------------
    # Structural Merge
    # --------------------------------------------------------

    merger = StructuralMerger()

    units = merger.merge(
        units
    )

    # --------------------------------------------------------
    # Primitive Discovery
    # --------------------------------------------------------

    selector = PrimitiveSelector()

    for unit in units:

        result = selector.predict(
            unit
        )

        unit.primitive = result["primitive"]
        unit.parameters = result["parameters"]
        unit.energy = result["energy"]

    # --------------------------------------------------------
    # Optimization
    # --------------------------------------------------------

    optimizer = StructuralOptimizer(
        merge_threshold=0.0,
        split_threshold=0.8,
        boundary_weight=0.5
    )

    units = optimizer.optimize(
        units
    )

    # --------------------------------------------------------
    # Primitive Re-discovery
    # --------------------------------------------------------

    selector = PrimitiveSelector()

    for unit in units:

        result = selector.predict(
            unit
        )

        unit.primitive = result["primitive"]

        unit.parameters = result["parameters"]

        unit.energy = result["energy"]


    # --------------------------------------------------------
    # Primitive Refinement
    # --------------------------------------------------------

    for unit in units:

        result = selector.predict(
            unit
        )

        unit.primitive = result["primitive"]
        unit.parameters = result["parameters"]
        unit.energy = result["energy"]

    # --------------------------------------------------------
    # Energy
    # --------------------------------------------------------

    energy_model = StructureEnergy()

    for unit in units:

        energy_model.compute(unit)

    # --------------------------------------------------------
    # Hierarchy
    # --------------------------------------------------------

    hierarchy = StructuralHierarchy()

    hierarchy.build(
        units
    )

    # --------------------------------------------------------
    # Relations
    # --------------------------------------------------------

    relation_graph = StructuralRelationGraph()

    relations = relation_graph.build(
        units
    )

    # --------------------------------------------------------
    # Object Assembly
    # --------------------------------------------------------

    assembler = StructuralObjectAssembly(
        threshold=0.6
    )

    objects = assembler.build(
        units,
        relations
    )

    object_relations = assembler.project_relations(
        units,
        objects,
        relations
    )

    # --------------------------------------------------------
    # Instances
    # --------------------------------------------------------

    instance_builder = StructuralInstanceBuilder()

    instances = instance_builder.build(
        units,
        objects
    )

    # --------------------------------------------------------
    # World State
    # --------------------------------------------------------

    world = StructuralWorldState()

    world.add_units(
        units
    )

    world.add_objects(
        objects
    )

    world.add_instances(
        instances
    )

    world.add_relations(
        object_relations
    )

    # --------------------------------------------------------
    # Embedding
    # --------------------------------------------------------

    # --------------------------------------------------------
    # Canonical Object Representation
    # --------------------------------------------------------

    embedding_model = StructuralEmbedding()

    embedding_objects = []

    for obj in objects:

        parameters = getattr(
            obj,
            "parameters",
            {}
        )

        # ----------------------------------------------------
        # Canonicalize parameters
        #
        # Struct3D v2.0:
        #
        # parameters MUST be dict.
        #
        # Legacy list[dict] is flattened only when necessary.
        # ----------------------------------------------------

        if parameters is None:

            parameters = {}

        elif isinstance(
            parameters,
            dict
        ):

            parameters = dict(
                parameters
            )

        elif isinstance(
            parameters,
            (list, tuple)
        ):

            merged = {}

            for item in parameters:

                if isinstance(
                    item,
                    dict
                ):

                    merged.update(
                        item
                    )

            parameters = merged

        else:

            parameters = {}

        embedding_objects.append({

            "primitive":
                getattr(
                    obj,
                    "primitives",
                    []
                ),

            "center":
                getattr(
                    obj,
                    "center",
                    np.zeros(3)
                ),

            "energy":
                getattr(
                    obj,
                    "energy",
                    0.0
                ),

            "parameters":
                parameters

        })

    if len(embedding_objects) > 0:

        embeddings = embedding_model.encode_objects(
            embedding_objects
        )

    else:

        embeddings = np.empty(
            (0, 0)
        )

    # --------------------------------------------------------
    # Prototype
    # --------------------------------------------------------

    prototype_memory = StructuralPrototypeMemory(
        threshold=0.75
    )

    for i, obj in enumerate(objects):

        if i >= len(embeddings):
            continue

        embedding = embeddings[i]

        primitive_list = getattr(
            obj,
            "primitives",
            []
        )

        if isinstance(
            primitive_list,
            list
        ) and len(primitive_list) > 0:

            primitive = primitive_list[0]

        else:

            primitive = "unknown"

        prototype_memory.process(
            embedding,
            primitive
        )

    prototype_memory.consolidate()

    # --------------------------------------------------------
    # Generalization
    # --------------------------------------------------------

    generalizer = PrototypeGeneralizer(
        threshold=0.5
    )

    concepts = generalizer.generalize(
        prototype_memory.prototypes,
        embeddings
    )

    # --------------------------------------------------------
    # Categories
    # --------------------------------------------------------

    category_model = StructuralCategoryEmergence(
        threshold=0.75
    )

    categories = category_model.build(
        concepts
    )

    # --------------------------------------------------------
    # Reasoning
    # --------------------------------------------------------

    reasoner = StructuralReasonerV2()

    reasoning = reasoner.infer(
        objects,
        relations
    )

    world.add_reasoning(
        reasoning
    )

    # --------------------------------------------------------
    # Prototypes / concepts / categories
    # --------------------------------------------------------

    world.add_prototypes(
        prototype_memory.prototypes
    )

    world.add_concepts(
        concepts
    )

    world.add_categories(
        categories
    )

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    world.set_metadata(
        "pipeline",
        "Struct3D-v2.0-end-to-end"
    )

    world.set_metadata(
        "input_points",
        int(points.shape[0])
    )

    # --------------------------------------------------------
    # Cognition
    # --------------------------------------------------------

    cognition = StructuralCognition()

    # Cognition is deliberately evaluated separately.
    # The canonical world state remains the source of truth.

    cognition_result = None

    return {
        "field": field,
        "graph": graph,
        "units": units,
        "relations": relations,
        "objects": objects,
        "instances": instances,
        "world": world,
        "embeddings": embeddings,
        "prototypes": prototype_memory.prototypes,
        "concepts": concepts,
        "categories": categories,
        "reasoning": reasoning,
        "cognition": cognition_result
    }


# ============================================================
# Validation
# ============================================================

def validate_pipeline(result):

    world = result["world"]

    validator = WorldStateValidator()

    validation = validator.validate(
        world
    )

    if not validation["valid"]:

        raise RuntimeError(
            "World validation failed: {}".format(
                validation["errors"]
            )
        )

    return validation


# ============================================================
# Main
# ============================================================

def main():

    print("\n")
    print("=" * 60)
    print("Struct3D v2.0 End-to-End Validation")
    print("=" * 60)

    # --------------------------------------------------------
    # Input
    # --------------------------------------------------------

    stage("[1] Input")

    points = load_data()

    print(
        "Input:",
        points.shape
    )

    success("Input")

    # --------------------------------------------------------
    # Geometry
    # --------------------------------------------------------

    stage("[2] Geometry")

    try:

        result = run_pipeline(
            points
        )

        success("Geometry + Structural Pipeline")

    except Exception as exc:

        failure(
            "Geometry + Structural Pipeline",
            exc
        )

        return 1

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    stage("[3] Structural Statistics")

    world = result["world"]

    print(
        "units:",
        len(world.units)
    )

    print(
        "objects:",
        len(world.objects)
    )

    print(
        "instances:",
        len(world.instances)
    )

    print(
        "relations:",
        len(world.relations)
    )

    print(
        "reasoning:",
        len(world.reasoning)
    )

    print(
        "prototypes:",
        len(world.prototypes)
    )

    print(
        "concepts:",
        len(world.concepts)
    )

    print(
        "categories:",
        len(world.categories)
    )

    success("Structural Statistics")

    # --------------------------------------------------------
    # World Validation
    # --------------------------------------------------------

    stage("[4] World State Validation")

    try:

        validation = validate_pipeline(
            result
        )

        print(
            "Status:",
            "PASS"
            if validation["valid"]
            else "FAIL"
        )

        print(
            "Errors:",
            len(validation["errors"])
        )

        print(
            "Warnings:",
            len(validation["warnings"])
        )

        success("World State Validation")

    except Exception as exc:

        failure(
            "World State Validation",
            exc
        )

        return 1

    # --------------------------------------------------------
    # Persistence
    # --------------------------------------------------------

    stage("[5] Persistence")

    path = os.path.join(
        ROOT,
        "data",
        "world_state_v20_end_to_end.pkl"
    )

    world.save(
        path
    )

    print(
        "Saved:",
        path
    )

    loaded = StructuralWorldState.load(
        path
    )

    validator = WorldStateValidator()

    loaded_validation = validator.validate(
        loaded
    )

    if not loaded_validation["valid"]:

        print(
            "Loaded state invalid"
        )

        validator.show(
            loaded_validation
        )

        return 1

    success("Persistence")

    # --------------------------------------------------------
    # Canonical Equality
    # --------------------------------------------------------

    stage("[6] Canonical Equality")

    def canonical_state(w):

        data = w.to_dict()

        return data

    state_a = canonical_state(
        world
    )

    state_b = canonical_state(
        loaded
    )

    if state_a != state_b:

        print(
            "Canonical equality: FAIL"
        )

        return 1

    print(
        "Canonical equality: PASS"
    )

    success("Canonical Equality")

    # --------------------------------------------------------
    # Deterministic Replay
    # --------------------------------------------------------

    stage("[7] Deterministic Replay")

    result_a = run_pipeline(
        points
    )

    result_b = run_pipeline(
        points
    )

    state_a = canonical_state(
        result_a["world"]
    )

    state_b = canonical_state(
        result_b["world"]
    )

    if state_a != state_b:

        print(
            "Replay equality: FAIL"
        )

        return 1

    print(
        "Replay equality: PASS"
    )

    success("Deterministic Replay")

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    stage("[8] Final Result")

    failed = [
        name
        for name, ok in RESULTS.items()
        if not ok
    ]

    if failed:

        print(
            "FAILED:",
            failed
        )

        return 1

    print(
        "All End-to-End Tests: PASS"
    )

    print()
    print("=" * 60)
    print("Struct3D v2.0")
    print("END-TO-END STATUS: PASS")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(
        main()
    )
