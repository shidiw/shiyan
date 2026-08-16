import numpy as np


# =====================================================
# Geometry
# =====================================================

from geometry.field import GeometryField


# =====================================================
# Graph
# =====================================================

from graph.relation import StructuralGraph


# =====================================================
# Structural Units
# =====================================================

from structure.graph_cluster import (
    GraphStructuralCluster
)


from structure.merge import (
    StructuralMerger
)


from structure.optimize import (
    StructuralOptimizer
)


from structure.primitive_selector import (
    PrimitiveSelector
)


from structure.energy import (
    StructureEnergy
)


# =====================================================
# Structure
# =====================================================

from structure.hierarchy import (
    StructuralHierarchy
)


from structure.relation import (
    StructuralRelationGraph
)


from structure.assembly import (
    StructuralObjectAssembly
)


from structure.instance import (
    StructuralInstanceBuilder
)


# =====================================================
# World Model
# =====================================================

from structure.world_model import (
    StructuralWorldModel
)


from structure.scene_graph import (
    StructuralSceneGraph
)


from structure.memory import (
    StructuralMemory
)


# =====================================================
# Prototype
# =====================================================

from structure.object_embedding import (
    StructuralEmbedding
)


from structure.prototype_memory import (
    StructuralPrototypeMemory
)


from structure.prototype_generalization import (
    PrototypeGeneralizer
)


from structure.category_emergence import (
    StructuralCategoryEmergence
)


# =====================================================
# Reasoning
# =====================================================

from structure.reasoning_v2 import (
    StructuralReasonerV2
)


from structure.cognition import (
    StructuralCognition
)


# =====================================================
# Load Data
# =====================================================

def load_data():

    points = np.load(
        "data/primitives.npy"
    )

    return points


# =====================================================
# Main
# =====================================================

def main():

    # =================================================
    # Load
    # =================================================

    points = load_data()

    print(
        "Input:",
        points.shape
    )


    # =================================================
    # Geometry Field
    # =================================================

    field_model = GeometryField(
        points,
        k=15
    )

    field = field_model.compute()

    print(
        "\nGeometry Field Done"
    )


    # =================================================
    # Structural Graph
    # =================================================

    print(
        "\nStructural Graph"
    )

    graph_model = StructuralGraph(
        k=30
    )

    graph = graph_model.build(
        points,
        field["normals"],
        field["curvature"]
    )

    graph_model.statistics(
        graph
    )


    # =================================================
    # Graph Structural Units
    # =================================================

    print(
        "\nGraph Structural Units"
    )

    cluster = GraphStructuralCluster(
        threshold=0.25,
        min_points=200
    )

    units = cluster.extract(
        points,
        graph
    )

    cluster.statistics(
        units
    )


    # =================================================
    # Structural Merge
    # =================================================

    merger = StructuralMerger()

    units = merger.merge(
        units
    )

    print(
        "\nAfter Structural Merge"
    )

    print(
        "Units:",
        len(units)
    )


    # =================================================
    # Primitive Discovery
    # =================================================

    selector = PrimitiveSelector()

    print(
        "\nInitial Primitive"
    )

    for u in units:

        result = selector.predict(
            u
        )

        u.primitive = result["primitive"]

        u.parameters = result["parameters"]

        u.energy = result["energy"]

        print(
            u.primitive,
            u.parameters
        )


    # =================================================
    # Structural Optimization
    # =================================================

    optimizer = StructuralOptimizer(
        merge_threshold=0.0,
        split_threshold=0.8,
        boundary_weight=0.5
    )

    units = optimizer.optimize(
        units
    )


    # =================================================
    # Primitive Refinement
    # =================================================

    print(
        "\nPrimitive Refinement"
    )

    for u in units:

        result = selector.predict(
            u
        )

        u.primitive = result["primitive"]

        u.parameters = result["parameters"]

        u.energy = result["energy"]

        print()

        print(
            "Primitive:",
            u.primitive
        )

        print(
            "Energy:",
            u.energy
        )

        print(
            "Parameters:",
            u.parameters
        )


    # =================================================
    # Energy
    # =================================================

    print(
        "\nEnergy"
    )

    energy = StructureEnergy()

    for u in units:

        print(
            u.primitive,
            energy.compute(u)
        )


    # =================================================
    # Hierarchy
    # =================================================

    hierarchy = StructuralHierarchy()

    hierarchy.build(
        units
    )

    print(
        "\nStructural Hierarchy"
    )

    hierarchy.show()


    # =================================================
    # Relation Graph
    # =================================================

    relation_graph = StructuralRelationGraph()

    relations = relation_graph.build(
        units
    )

    print(
        "\nStructural Relation Graph"
    )

    relation_graph.show()

    relation_graph.statistics()


    # =================================================
    # Object Assembly
    # =================================================

    print(
        "\nStructural Object Assembly"
    )

    assembler = StructuralObjectAssembly(
        threshold=0.6
    )

    objects = assembler.build(
        units,
        relations
    )

    assembler.show(
        objects
    )

    assembler.statistics(
        objects
    )


    # =================================================
    # Instance Segmentation
    # =================================================

    print(
        "\nStructural Instance Segmentation"
    )

    instance_builder = StructuralInstanceBuilder()

    instances = instance_builder.build(
        units,
        objects
    )

    instance_builder.statistics(
        instances
    )


    # =================================================
    # Structural World Model
    # =================================================

    print(
        "\nStructural World Model"
    )

    world = StructuralWorldModel()

    world.add_objects(
        objects
    )

    world.add_instances(
        instances
    )

    world.add_relations(
        relations
    )

    world.add_units(
        units
    )

    world.show()

    world.statistics()


    # =================================================
    # Structural Scene Graph
    # =================================================

    print(
        "\nStructural Scene Graph"
    )

    scene_graph = StructuralSceneGraph()

    scene_graph.build(
        objects,
        relations
    )

    scene_graph.show()

    scene_graph.statistics()


    # =================================================
    # Structural Memory
    # =================================================

    print(
        "\nStructural Memory"
    )

    memory = StructuralMemory()

    memory.update(
        objects,
        relations
    )

    memory.save()

    memory.show()

    memory.statistics()


    # =====================================================
    # Structural Embedding
    # =====================================================

    print(
        "\nStructural Embedding"
    )

    embedding_model = StructuralEmbedding()


    embedding_objects = []


    for obj in objects:

        embedding_objects.append({

            "primitive":
            obj.primitives,

            "center":
            obj.center,

            "energy":
            obj.energy,

            "parameters":
            obj.parameters[0]

        })


    embeddings = embedding_model.encode_objects(
        embedding_objects
    )


    print(
        "Embedding Shape:",
        embeddings.shape
    )


    # =====================================================
    # Structural Prototype Memory
    # =====================================================

    print(
        "\nStructural Prototype Memory"
    )


    prototype_memory = StructuralPrototypeMemory(
        threshold=0.75
    )


    # -----------------------------------------------------
    # Process every object
    # -----------------------------------------------------

    for i, obj in enumerate(objects):


        emb = embeddings[i]


        primitive = obj.primitives[0]


        result = prototype_memory.process(
            emb,
            primitive
        )


        print(
            "Object",
            i,
            "->",
            result["status"],
            "score:",
            result["score"]
        )


    # -----------------------------------------------------
    # Prototype Consolidation
    # -----------------------------------------------------

    prototype_memory.consolidate()


    # -----------------------------------------------------
    # Persistent Save
    # -----------------------------------------------------

    prototype_memory.save()


    # -----------------------------------------------------
    # Show
    # -----------------------------------------------------

    prototype_memory.show()


    # =====================================================
    # Prototype Generalization
    # =====================================================

    print(
        "\nStructural Prototype Generalization"
    )


    generalizer = PrototypeGeneralizer(
        threshold=0.5
    )


    concepts = generalizer.generalize(
        prototype_memory.prototypes,
        embeddings
    )


    generalizer.show(
        concepts
    )


    # =====================================================
    # Structural Category Emergence
    # =====================================================

    print(
        "\nStructural Category Emergence"
    )


    category_model = StructuralCategoryEmergence(
        threshold=0.75
    )


    categories = category_model.build(
        concepts
    )


    category_model.show(
        categories
    )


    print(
        "\nEmergent Categories"
    )


    for category in categories:

        print(
            category["id"],
            category["instances"]
        )


    # =====================================================
    # Structural Reasoning
    # =====================================================

    print(
        "\nStructural Reasoning V2"
    )


    reasoner = StructuralReasonerV2()


    reasoning_v2 = reasoner.infer(
        objects,
        relations
    )


    reasoner.show(
        reasoning_v2
    )


    # =====================================================
    # Structural Cognition
    # =====================================================

    print(
        "\nStructural Cognition"
    )


    cognition = StructuralCognition()


    understanding = cognition.analyze(
        world,
        scene_graph,
        memory,
        reasoning_v2
    )


    cognition.show(
        understanding
    )


    # =================================================
    # Final Structural Units
    # =================================================

    print(
        "\nFinal Structural Units"
    )


    for i, u in enumerate(units):

        print(
            "\nUnit",
            i
        )

        print(
            u.info()
        )

        print(
            "Parameters:",
            u.parameters
        )


# =====================================================
# Entry
# =====================================================

if __name__ == "__main__":

    main()