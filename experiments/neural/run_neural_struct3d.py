#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
======================================================================
Neural Struct3D v1.1
Local Geometry Refinement
======================================================================

Version chain
-------------

    Struct3D v3.6
        Canonical Structural Form
              |
    Struct3D v3.7
        Structural Invariant
              |
    Struct3D v3.8
        Structural Distance
              |
    Struct3D v3.9
        Structural Matching
              |
    Struct3D v4.0
        23D Structural Representation
              |
    Neural Struct3D v1.0
        Global Distance + Local Rank
              |
    Neural Struct3D v1.1
        Local Geometry Refinement

----------------------------------------------------------------------

Core mapping
----------------------------------------------------------------------

        W
        |
        v
    phi(W) in R^23
        |
        v
    Structural Encoder
        |
        v
      z in R^64
        |
        +--------------------+
        |                    |
        v                    v
    Global Geometry      Local Geometry
        |                    |
        +---------+----------+
                  |
                  v
          Refined Structural
             Latent Space

----------------------------------------------------------------------

v1.1 objective
----------------------------------------------------------------------

    L =
        lambda_recon
            * L_recon

      + lambda_global
            * L_global_distance

      + lambda_local
            * L_local_geometry

      + lambda_rank
            * L_local_rank

      + lambda_mono
            * L_local_monotonic

      + lambda_latent
            * L_latent

----------------------------------------------------------------------

Important implementation change
----------------------------------------------------------------------

v1.0 used Python loops for local rank and monotonic losses.

v1.1 replaces them with vectorized tensor operations.

Instead of:

    for i in range(N):
        for p in range(K):
            ...

we construct:

    local_neighbors : [N, K]

and directly gather:

    D_R_local : [N, K]
    D_Z_local : [N, K]

This makes CPU training substantially faster.

----------------------------------------------------------------------

CPU only.
No CUDA.
No Open3D.
No external dataset.
No large corpus.

======================================================================
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import random
import sys
import time

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


# ======================================================================
# Configuration
# ======================================================================

VERSION = "1.1"
STRUCT3D_VERSION = "4.0"

SEED = 20260814

INPUT_DIM = 23
LATENT_DIM = 64

HIDDEN_DIM_1 = 128
HIDDEN_DIM_2 = 128

# ----------------------------------------------------------------------
# Dataset
# ----------------------------------------------------------------------

TRAIN_SAMPLES = 800

# v1.1 intentionally uses fewer epochs.
# Local geometry is now vectorized.
TRAIN_EPOCHS = 150

LEARNING_RATE = 1e-3


# ======================================================================
# v1.1 Loss Weights
# ======================================================================

LAMBDA_RECON = 1.0

LAMBDA_DISTANCE = 1.0

LAMBDA_LOCAL = 1.0

LAMBDA_RANK = 0.50

LAMBDA_MONOTONIC = 0.25

LAMBDA_LATENT = 1e-4


# ======================================================================
# Local Geometry
# ======================================================================

# Number of local neighbors used by v1.1.
LOCAL_K = 16

# Number of anchors sampled during training.
#
# None means all anchors.
#
# For CPU speed, 256 is enough for the synthetic structural dataset.
LOCAL_ANCHORS = 256

RANK_MARGIN = 0.01

EPS = 1e-8


# ======================================================================
# Validation
# ======================================================================

RECONSTRUCTION_THRESHOLD = 0.08

DISTANCE_RELATIVE_ERROR_THRESHOLD = 0.20

LOCAL_DISTANCE_RELATIVE_ERROR_THRESHOLD = 0.20

LOCAL_NEIGHBOR_RECALL_THRESHOLD = 0.75

LOCAL_RANK_ACCURACY_THRESHOLD = 0.75


# ======================================================================
# Display
# ======================================================================

PRINT_EVERY = 10

DEVICE = torch.device("cpu")


# ======================================================================
# Determinism
# ======================================================================

def seed_everything(seed: int = SEED) -> None:

    random.seed(seed)

    torch.manual_seed(seed)

    try:
        torch.use_deterministic_algorithms(True)
    except Exception:
        pass

    # One thread is often more reproducible on small CPU workloads.
    try:
        torch.set_num_threads(1)
    except Exception:
        pass


seed_everything()


# ======================================================================
# Printing
# ======================================================================

def line() -> None:
    print("-" * 68)


def header(title: str) -> None:
    print()
    line()
    print(title)
    line()


def passed(name: str) -> None:
    print(f"[PASS] {name}")


def failed(name: str) -> None:
    print(f"[FAIL] {name}")


# ======================================================================
# Stable JSON / Hash
# ======================================================================

def stable_json(obj: Any) -> str:

    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def stable_hash(obj: Any) -> str:

    payload = stable_json(obj).encode("utf-8")

    return hashlib.sha256(payload).hexdigest()


# ======================================================================
# Structural World
# ======================================================================

@dataclass
class Unit:

    uid: str
    primitive: str
    scale: float = 1.0
    fit: float = 0.1


@dataclass
class ObjectNode:

    oid: str
    name: str
    units: Tuple[str, ...]


@dataclass
class InstanceNode:

    iid: str
    object_id: str


@dataclass
class Relation:

    rid: str
    source: str
    target: str
    relation_type: str
    confidence: float


@dataclass
class World:

    units: Dict[str, Unit]
    objects: Dict[str, ObjectNode]
    instances: Dict[str, InstanceNode]
    relations: Dict[str, Relation]


# ======================================================================
# Base World
# ======================================================================

def make_base_world() -> World:

    units = {

        "U0": Unit(
            uid="U0",
            primitive="plane",
        ),

        "U1": Unit(
            uid="U1",
            primitive="sphere",
        ),

        "U2": Unit(
            uid="U2",
            primitive="plane",
        ),

        "U3": Unit(
            uid="U3",
            primitive="sphere",
        ),
    }

    objects = {

        "O0": ObjectNode(
            oid="O0",
            name="assembly",
            units=("U0", "U1"),
        ),

        "O1": ObjectNode(
            oid="O1",
            name="assembly",
            units=("U2", "U3"),
        ),
    }

    instances = {

        "I0": InstanceNode(
            iid="I0",
            object_id="O0",
        ),

        "I1": InstanceNode(
            iid="I1",
            object_id="O1",
        ),
    }

    relations = {

        "R0": Relation(
            rid="R0",
            source="O0",
            target="O1",
            relation_type="adjacent",
            confidence=0.85,
        ),

        "R1": Relation(
            rid="R1",
            source="O1",
            target="O0",
            relation_type="supports",
            confidence=0.90,
        ),
    }

    return World(
        units=units,
        objects=objects,
        instances=instances,
        relations=relations,
    )


def clone_world(world: World) -> World:

    return copy.deepcopy(world)


# ======================================================================
# Structural Constants
# ======================================================================

PRIMITIVES = (
    "plane",
    "sphere",
    "cylinder",
)

RELATION_TYPES = (
    "adjacent",
    "supports",
    "contains",
)


# ======================================================================
# Structural Statistics
# ======================================================================

def primitive_histogram(
    world: World,
) -> List[float]:

    counts = {
        p: 0
        for p in PRIMITIVES
    }

    for unit in world.units.values():

        if unit.primitive not in counts:
            counts[unit.primitive] = 0

        counts[unit.primitive] += 1

    total = max(
        len(world.units),
        1,
    )

    return [
        counts.get(p, 0) / total
        for p in PRIMITIVES
    ]


def object_histogram(
    world: World,
) -> List[float]:

    values = [
        len(obj.units)
        for obj in world.objects.values()
    ]

    if not values:
        return [
            0.0,
            0.0,
            0.0,
        ]

    return [

        sum(
            v == 1
            for v in values
        ) / len(values),

        sum(
            v == 2
            for v in values
        ) / len(values),

        sum(
            v >= 3
            for v in values
        ) / len(values),
    ]


def instance_occupancy(
    world: World,
) -> Tuple[float, float, float]:

    if not world.instances:

        return (
            0.0,
            0.0,
            0.0,
        )

    counts = {
        oid: 0
        for oid in world.objects
    }

    for inst in world.instances.values():

        if inst.object_id not in counts:
            counts[inst.object_id] = 0

        counts[inst.object_id] += 1

    values = list(
        counts.values()
    )

    return (

        sum(
            v == 0
            for v in values
        ) / len(values),

        sum(
            v == 1
            for v in values
        ) / len(values),

        sum(
            v >= 2
            for v in values
        ) / len(values),
    )


def relation_type_histogram(
    world: World,
) -> List[float]:

    counts = {
        r: 0
        for r in RELATION_TYPES
    }

    for rel in world.relations.values():

        if rel.relation_type not in counts:
            counts[rel.relation_type] = 0

        counts[rel.relation_type] += 1

    total = max(
        len(world.relations),
        1,
    )

    return [
        counts.get(r, 0) / total
        for r in RELATION_TYPES
    ]


def relation_confidence_statistics(
    world: World,
) -> Tuple[float, float, float]:

    if not world.relations:

        return (
            0.0,
            0.0,
            0.0,
        )

    values = [
        float(r.confidence)
        for r in world.relations.values()
    ]

    mean = sum(values) / len(values)

    variance = sum(
        (x - mean) ** 2
        for x in values
    ) / len(values)

    return (
        mean,
        math.sqrt(variance),
        min(values),
    )


# ======================================================================
# Struct3D Representation
# ======================================================================

def structural_representation(
    world: World,
) -> List[float]:

    features: List[float] = []

    features.extend(
        primitive_histogram(world)
    )

    features.extend(
        object_histogram(world)
    )

    num_objects = len(world.objects)

    if num_objects == 0:

        avg_units = 0.0
        max_units = 0.0
        min_units = 0.0

    else:

        sizes = [
            len(obj.units)
            for obj in world.objects.values()
        ]

        avg_units = sum(
            sizes
        ) / len(sizes)

        max_units = max(sizes)

        min_units = min(sizes)

    features.extend([

        num_objects / 4.0,

        avg_units / 4.0,

        max_units / 4.0,
    ])

    features.extend(
        relation_type_histogram(world)
    )

    mean_conf, std_conf, min_conf = \
        relation_confidence_statistics(
            world
        )

    features.extend([

        mean_conf,

        std_conf,

        min_conf,
    ])

    features.extend(
        instance_occupancy(world)
    )

    features.extend([

        len(world.units) / 4.0,

        len(world.objects) / 4.0,

        len(world.instances) / 4.0,

        len(world.relations) / 4.0,

        len(world.objects)
        /
        max(
            len(world.instances),
            1,
        ),
    ])

    if len(features) != INPUT_DIM:

        raise RuntimeError(
            f"Expected {INPUT_DIM} dimensions, "
            f"got {len(features)}"
        )

    return [
        float(v)
        for v in features
    ]


def representation_hash(
    world: World,
) -> str:

    rep = structural_representation(
        world
    )

    rounded = [
        round(
            float(x),
            10,
        )
        for x in rep
    ]

    return stable_hash(
        rounded
    )


# ======================================================================
# Structural Distance
# ======================================================================

def structural_distance(
    world_a: World,
    world_b: World,
) -> float:

    a = torch.tensor(
        structural_representation(world_a),
        dtype=torch.float64,
    )

    b = torch.tensor(
        structural_representation(world_b),
        dtype=torch.float64,
    )

    return float(
        torch.linalg.vector_norm(
            a - b
        ).item()
    )


# ======================================================================
# Mutations
# ======================================================================

def mutate_primitive(
    world: World,
) -> World:

    result = clone_world(world)

    result.units["U0"].primitive = \
        "cylinder"

    return result


def mutate_object_composition(
    world: World,
) -> World:

    result = clone_world(world)

    result.objects["O0"].units = (
        "U0",
    )

    result.objects["O1"].units = (
        "U1",
        "U2",
        "U3",
    )

    return result


def mutate_instance_composition(
    world: World,
) -> World:

    result = clone_world(world)

    result.instances["I0"].object_id = \
        "O1"

    return result


def mutate_relation_type(
    world: World,
) -> World:

    result = clone_world(world)

    result.relations[
        "R0"
    ].relation_type = "contains"

    return result


def mutate_relation_confidence(
    world: World,
) -> World:

    result = clone_world(world)

    result.relations[
        "R0"
    ].confidence = 0.25

    return result


def mutate_relation_deletion(
    world: World,
) -> World:

    result = clone_world(world)

    del result.relations["R1"]

    return result


# ======================================================================
# World Transformations
# ======================================================================

def reorder_world(
    world: World,
) -> World:

    result = clone_world(world)

    result.units = dict(
        reversed(
            list(
                result.units.items()
            )
        )
    )

    result.objects = dict(
        reversed(
            list(
                result.objects.items()
            )
        )
    )

    result.instances = dict(
        reversed(
            list(
                result.instances.items()
            )
        )
    )

    result.relations = dict(
        reversed(
            list(
                result.relations.items()
            )
        )
    )

    return result


def relabel_units(
    world: World,
) -> World:

    result = clone_world(world)

    mapping = {
        "U0": "U1",
        "U1": "U0",
        "U2": "U3",
        "U3": "U2",
    }

    new_units = {}

    for old_id, unit in result.units.items():

        new_id = mapping[old_id]

        new_units[new_id] = Unit(
            uid=new_id,
            primitive=unit.primitive,
            scale=unit.scale,
            fit=unit.fit,
        )

    result.units = new_units

    new_objects = {}

    for oid, obj in result.objects.items():

        new_objects[oid] = ObjectNode(
            oid=oid,
            name=obj.name,
            units=tuple(
                mapping[u]
                for u in obj.units
            ),
        )

    result.objects = new_objects

    return result


def relabel_objects(
    world: World,
) -> World:

    result = clone_world(world)

    mapping = {
        "O0": "O1",
        "O1": "O0",
    }

    new_objects = {}

    for old_id, obj in result.objects.items():

        new_id = mapping[old_id]

        new_objects[new_id] = ObjectNode(
            oid=new_id,
            name=obj.name,
            units=obj.units,
        )

    result.objects = new_objects

    new_instances = {}

    for iid, inst in result.instances.items():

        new_instances[iid] = InstanceNode(
            iid=iid,
            object_id=mapping[
                inst.object_id
            ],
        )

    result.instances = new_instances

    new_relations = {}

    for rid, rel in result.relations.items():

        new_relations[rid] = Relation(
            rid=rid,
            source=mapping.get(
                rel.source,
                rel.source,
            ),
            target=mapping.get(
                rel.target,
                rel.target,
            ),
            relation_type=rel.relation_type,
            confidence=rel.confidence,
        )

    result.relations = new_relations

    return result


def relabel_instances(
    world: World,
) -> World:

    result = clone_world(world)

    mapping = {
        "I0": "I1",
        "I1": "I0",
    }

    new_instances = {}

    for old_id, inst in result.instances.items():

        new_id = mapping[old_id]

        new_instances[new_id] = InstanceNode(
            iid=new_id,
            object_id=inst.object_id,
        )

    result.instances = new_instances

    return result


def relabel_relations(
    world: World,
) -> World:

    result = clone_world(world)

    mapping = {
        "R0": "R1",
        "R1": "R0",
    }

    new_relations = {}

    for old_id, rel in result.relations.items():

        new_id = mapping[old_id]

        new_relations[new_id] = Relation(
            rid=new_id,
            source=rel.source,
            target=rel.target,
            relation_type=rel.relation_type,
            confidence=rel.confidence,
        )

    result.relations = new_relations

    return result


# ======================================================================
# Random Structural World
# ======================================================================

def random_structural_world(
    rng: random.Random,
) -> World:

    world = make_base_world()

    for uid in world.units:

        if rng.random() < 0.35:

            world.units[
                uid
            ].primitive = rng.choice(
                PRIMITIVES
            )

    unit_ids = list(
        world.units.keys()
    )

    for oid in world.objects:

        size = rng.randint(
            1,
            len(unit_ids),
        )

        selected = rng.sample(
            unit_ids,
            size,
        )

        world.objects[
            oid
        ].units = tuple(
            sorted(selected)
        )

    object_ids = list(
        world.objects.keys()
    )

    for iid in world.instances:

        world.instances[
            iid
        ].object_id = rng.choice(
            object_ids
        )

    for rid in world.relations:

        world.relations[
            rid
        ].relation_type = rng.choice(
            RELATION_TYPES
        )

        world.relations[
            rid
        ].confidence = round(
            rng.uniform(
                0.1,
                1.0,
            ),
            3,
        )

    return world


# ======================================================================
# Dataset
# ======================================================================

def build_training_worlds(
    n: int = TRAIN_SAMPLES,
) -> List[World]:

    rng = random.Random(
        SEED
    )

    worlds = []

    base = make_base_world()

    worlds.append(base)

    mutations = [

        mutate_primitive,

        mutate_object_composition,

        mutate_instance_composition,

        mutate_relation_type,

        mutate_relation_confidence,

        mutate_relation_deletion,
    ]

    for mutation in mutations:

        worlds.append(
            mutation(base)
        )

    seen = {
        tuple(
            structural_representation(w)
        )
        for w in worlds
    }

    while len(worlds) < n:

        world = random_structural_world(
            rng
        )

        key = tuple(
            structural_representation(world)
        )

        if key in seen:
            continue

        seen.add(key)

        worlds.append(world)

    return worlds


def worlds_to_tensor(
    worlds: List[World],
) -> torch.Tensor:

    return torch.tensor(
        [
            structural_representation(w)
            for w in worlds
        ],
        dtype=torch.float32,
        device=DEVICE,
    )


# ======================================================================
# Neural Model
# ======================================================================

class StructuralEncoder(
    nn.Module
):

    def __init__(
        self,
        input_dim: int = INPUT_DIM,
        latent_dim: int = LATENT_DIM,
    ):

        super().__init__()

        self.net = nn.Sequential(

            nn.Linear(
                input_dim,
                HIDDEN_DIM_1,
            ),

            nn.ReLU(),

            nn.Linear(
                HIDDEN_DIM_1,
                HIDDEN_DIM_2,
            ),

            nn.ReLU(),

            nn.Linear(
                HIDDEN_DIM_2,
                latent_dim,
            ),
        )

    def forward(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:

        return self.net(x)


class StructuralDecoder(
    nn.Module
):

    def __init__(
        self,
        latent_dim: int = LATENT_DIM,
        output_dim: int = INPUT_DIM,
    ):

        super().__init__()

        self.net = nn.Sequential(

            nn.Linear(
                latent_dim,
                HIDDEN_DIM_2,
            ),

            nn.ReLU(),

            nn.Linear(
                HIDDEN_DIM_2,
                HIDDEN_DIM_1,
            ),

            nn.ReLU(),

            nn.Linear(
                HIDDEN_DIM_1,
                output_dim,
            ),
        )

    def forward(
        self,
        z: torch.Tensor,
    ) -> torch.Tensor:

        return self.net(z)


class NeuralStruct3D(
    nn.Module
):

    def __init__(
        self,
        input_dim: int = INPUT_DIM,
        latent_dim: int = LATENT_DIM,
    ):

        super().__init__()

        self.encoder = StructuralEncoder(
            input_dim=input_dim,
            latent_dim=latent_dim,
        )

        self.decoder = StructuralDecoder(
            latent_dim=latent_dim,
            output_dim=input_dim,
        )

    def encode(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:

        return self.encoder(x)

    def decode(
        self,
        z: torch.Tensor,
    ) -> torch.Tensor:

        return self.decoder(z)

    def forward(
        self,
        x: torch.Tensor,
    ) -> Tuple[
        torch.Tensor,
        torch.Tensor,
    ]:

        z = self.encode(x)

        x_hat = self.decode(z)

        return z, x_hat


# ======================================================================
# Pairwise Distance
# ======================================================================

def pairwise_distance(
    x: torch.Tensor,
) -> torch.Tensor:

    return torch.cdist(
        x,
        x,
        p=2,
    )


# ======================================================================
# Local Neighborhood Construction
# ======================================================================

def build_local_neighbors(
    d_x: torch.Tensor,
    k: int = LOCAL_K,
) -> torch.Tensor:

    """
    Return nearest-neighbor indices.

    Input:
        d_x : [N, N]

    Output:
        neighbors : [N, K]

    The diagonal is excluded.
    """

    n = d_x.shape[0]

    k = min(
        k,
        max(n - 1, 1),
    )

    # Exclude self.
    diagonal = torch.eye(
        n,
        dtype=torch.bool,
        device=d_x.device,
    )

    masked = d_x.masked_fill(
        diagonal,
        float("inf"),
    )

    _, neighbors = torch.topk(
        masked,
        k=k,
        dim=1,
        largest=False,
        sorted=True,
    )

    return neighbors


# ======================================================================
# Global Distance Loss
# ======================================================================

def distance_loss_from_matrix(
    d_x: torch.Tensor,
    d_z: torch.Tensor,
) -> torch.Tensor:

    n = d_x.shape[0]

    mask = torch.triu(
        torch.ones(
            (n, n),
            dtype=torch.bool,
            device=d_x.device,
        ),
        diagonal=1,
    )

    target = d_x[mask]

    prediction = d_z[mask]

    return F.mse_loss(
        prediction,
        target,
    )


# ======================================================================
# Gather Local Distances
# ======================================================================

def gather_local_distances(
    d: torch.Tensor,
    neighbors: torch.Tensor,
) -> torch.Tensor:

    """
    d:
        [N, N]

    neighbors:
        [N, K]

    result:
        [N, K]
    """

    return torch.gather(
        d,
        1,
        neighbors,
    )


# ======================================================================
# v1.1 Local Geometry Loss
# ======================================================================

def local_geometry_loss(
    d_x_local: torch.Tensor,
    d_z_local: torch.Tensor,
) -> torch.Tensor:

    """
    Direct local metric refinement.

    Each anchor has K local structural neighbors.

    We normalize by the anchor's local structural radius
    to emphasize local geometry rather than absolute global scale.

        r_R(i,j) = D_R(i,j) / max(D_R(i,K), eps)

        r_Z(i,j) = D_Z(i,j) / max(D_Z(i,K), eps)

    The loss encourages:

        r_Z ~= r_R
    """

    radius_x = d_x_local[:, -1:].detach()

    radius_z = d_z_local[:, -1:]

    radius_x = torch.clamp(
        radius_x,
        min=EPS,
    )

    radius_z = torch.clamp(
        radius_z,
        min=EPS,
    )

    normalized_x = (
        d_x_local
        /
        radius_x
    )

    normalized_z = (
        d_z_local
        /
        radius_z
    )

    return F.smooth_l1_loss(
        normalized_z,
        normalized_x,
    )


# ======================================================================
# v1.1 Vectorized Local Rank Loss
# ======================================================================

def vectorized_local_rank_loss(
    d_x_local: torch.Tensor,
    d_z_local: torch.Tensor,
) -> torch.Tensor:

    """
    Vectorized local rank preservation.

    For every anchor we compare:

        nearest < farther

    instead of executing Python loops.

    d_x_local:
        [A, K]

    d_z_local:
        [A, K]
    """

    k = d_x_local.shape[1]

    if k < 2:

        return torch.zeros(
            (),
            device=d_x_local.device,
        )

    # Compare consecutive local neighbors.
    target_gap = (
        d_x_local[:, 1:]
        -
        d_x_local[:, :-1]
    )

    latent_gap = (
        d_z_local[:, 1:]
        -
        d_z_local[:, :-1]
    )

    valid = (
        target_gap
        >
        1e-6
    )

    violations = F.relu(
        RANK_MARGIN
        -
        latent_gap
    )

    # Weight closer structural comparisons more.
    weights = 1.0 / (
        target_gap.abs()
        + 0.05
    )

    weights = torch.clamp(
        weights,
        max=10.0,
    )

    weighted = (
        violations
        *
        weights
    )

    if valid.any():

        return weighted[
            valid
        ].mean()

    return torch.zeros(
        (),
        device=d_x_local.device,
    )


# ======================================================================
# v1.1 Vectorized Monotonic Loss
# ======================================================================

def vectorized_monotonic_loss(
    d_x_local: torch.Tensor,
    d_z_local: torch.Tensor,
) -> torch.Tensor:

    """
    Local monotonicity.

        D_R(i,j) < D_R(i,k)

        =>

        D_Z(i,j) < D_Z(i,k)
    """

    if d_x_local.shape[1] < 2:

        return torch.zeros(
            (),
            device=d_x_local.device,
        )

    structural_gap = (
        d_x_local[:, 1:]
        -
        d_x_local[:, :-1]
    )

    latent_gap = (
        d_z_local[:, 1:]
        -
        d_z_local[:, :-1]
    )

    valid = (
        structural_gap
        >
        1e-6
    )

    losses = F.relu(
        RANK_MARGIN
        -
        latent_gap
    )

    if valid.any():

        return losses[
            valid
        ].mean()

    return torch.zeros(
        (),
        device=d_x_local.device,
    )


# ======================================================================
# Training Result
# ======================================================================

@dataclass
class TrainingResult:

    initial_loss: float
    final_loss: float

    initial_reconstruction: float
    final_reconstruction: float

    initial_distance: float
    final_distance: float

    initial_local: float
    final_local: float

    initial_rank: float
    final_rank: float

    initial_monotonic: float
    final_monotonic: float

    epochs: int


# ======================================================================
# Training
# ======================================================================

def train_model(
    model: NeuralStruct3D,
    x: torch.Tensor,
    epochs: int = TRAIN_EPOCHS,
    lr: float = LEARNING_RATE,
) -> TrainingResult:

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=lr,
    )

    # --------------------------------------------------------------
    # Structural distance is fixed for the dataset.
    #
    # IMPORTANT:
    # We compute it ONCE, not every epoch.
    # --------------------------------------------------------------

    with torch.no_grad():

        d_x = pairwise_distance(
            x
        )

        neighbors_all = build_local_neighbors(
            d_x,
            LOCAL_K,
        )

    n = x.shape[0]

    anchor_count = min(
        LOCAL_ANCHORS,
        n,
    )

    # Fixed deterministic anchor set.
    anchor_indices = torch.linspace(
        0,
        n - 1,
        steps=anchor_count,
        device=x.device,
    ).long()

    neighbors = neighbors_all[
        anchor_indices
    ]

    d_x_local = torch.gather(
        d_x[
            anchor_indices
        ],
        1,
        neighbors,
    )

    initial = None
    final = None

    model.train()

    training_start = time.perf_counter()

    for epoch in range(
        1,
        epochs + 1,
    ):

        epoch_start = time.perf_counter()

        optimizer.zero_grad()

        z, x_hat = model(x)

        # ----------------------------------------------------------
        # Reconstruction
        # ----------------------------------------------------------

        reconstruction = F.mse_loss(
            x_hat,
            x,
        )

        # ----------------------------------------------------------
        # Global latent distance
        # ----------------------------------------------------------

        d_z = pairwise_distance(
            z
        )

        global_distance = distance_loss_from_matrix(
            d_x,
            d_z,
        )

        # ----------------------------------------------------------
        # Local latent distances
        # ----------------------------------------------------------

        d_z_local = torch.gather(
            d_z[
                anchor_indices
            ],
            1,
            neighbors,
        )

        # ----------------------------------------------------------
        # Local Geometry Refinement
        # ----------------------------------------------------------

        local_loss = local_geometry_loss(
            d_x_local,
            d_z_local,
        )

        # ----------------------------------------------------------
        # Local rank
        # ----------------------------------------------------------

        rank_loss = vectorized_local_rank_loss(
            d_x_local,
            d_z_local,
        )

        # ----------------------------------------------------------
        # Local monotonicity
        # ----------------------------------------------------------

        mono_loss = vectorized_monotonic_loss(
            d_x_local,
            d_z_local,
        )

        # ----------------------------------------------------------
        # Latent regularization
        # ----------------------------------------------------------

        latent_regularization = torch.mean(
            z ** 2
        )

        # ----------------------------------------------------------
        # Total
        # ----------------------------------------------------------

        total = (

            LAMBDA_RECON
            * reconstruction

            +

            LAMBDA_DISTANCE
            * global_distance

            +

            LAMBDA_LOCAL
            * local_loss

            +

            LAMBDA_RANK
            * rank_loss

            +

            LAMBDA_MONOTONIC
            * mono_loss

            +

            LAMBDA_LATENT
            * latent_regularization
        )

        total.backward()

        torch.nn.utils.clip_grad_norm_(
            model.parameters(),
            max_norm=10.0,
        )

        optimizer.step()

        record = {

            "total":
                float(
                    total.detach()
                ),

            "reconstruction":
                float(
                    reconstruction.detach()
                ),

            "distance":
                float(
                    global_distance.detach()
                ),

            "local":
                float(
                    local_loss.detach()
                ),

            "rank":
                float(
                    rank_loss.detach()
                ),

            "monotonic":
                float(
                    mono_loss.detach()
                ),
        }

        if initial is None:

            initial = record

        final = record

        # ----------------------------------------------------------
        # Progress
        # ----------------------------------------------------------

        should_print = (

            epoch == 1

            or

            epoch % PRINT_EVERY == 0

            or

            epoch == epochs
        )

        if should_print:

            now = time.perf_counter()

            elapsed = (
                now
                -
                training_start
            )

            avg_epoch = (
                elapsed
                /
                epoch
            )

            remaining = (
                epochs
                -
                epoch
            )

            eta = (
                remaining
                *
                avg_epoch
            )

            epoch_time = (
                now
                -
                epoch_start
            )

            print(
                f"Epoch {epoch:03d}/{epochs}: "
                f"total={record['total']:.8f} "
                f"recon={record['reconstruction']:.8f} "
                f"global={record['distance']:.8f} "
                f"local={record['local']:.8f} "
                f"rank={record['rank']:.8f} "
                f"mono={record['monotonic']:.8f} "
                f"| epoch={epoch_time:.2f}s "
                f"| ETA={eta:.1f}s"
            )

    return TrainingResult(

        initial_loss=
            initial["total"],

        final_loss=
            final["total"],

        initial_reconstruction=
            initial["reconstruction"],

        final_reconstruction=
            final["reconstruction"],

        initial_distance=
            initial["distance"],

        final_distance=
            final["distance"],

        initial_local=
            initial["local"],

        final_local=
            final["local"],

        initial_rank=
            initial["rank"],

        final_rank=
            final["rank"],

        initial_monotonic=
            initial["monotonic"],

        final_monotonic=
            final["monotonic"],

        epochs=epochs,
    )


# ======================================================================
# Latent Distance
# ======================================================================

def latent_distance(
    model: NeuralStruct3D,
    world_a: World,
    world_b: World,
) -> float:

    xa = torch.tensor(
        structural_representation(world_a),
        dtype=torch.float32,
        device=DEVICE,
    ).unsqueeze(0)

    xb = torch.tensor(
        structural_representation(world_b),
        dtype=torch.float32,
        device=DEVICE,
    ).unsqueeze(0)

    model.eval()

    with torch.no_grad():

        za = model.encode(xa)

        zb = model.encode(xb)

    return float(
        torch.linalg.vector_norm(
            za - zb
        )
    )


# ======================================================================
# Reconstruction
# ======================================================================

def reconstruction_error(
    model: NeuralStruct3D,
    world: World,
) -> float:

    x = torch.tensor(
        structural_representation(world),
        dtype=torch.float32,
        device=DEVICE,
    ).unsqueeze(0)

    model.eval()

    with torch.no_grad():

        _, x_hat = model(x)

    return float(
        torch.mean(
            torch.abs(
                x_hat - x
            )
        )
    )


# ======================================================================
# Local Geometry Evaluation
# ======================================================================

def evaluate_local_geometry(
    model: NeuralStruct3D,
    dataset: torch.Tensor,
    k: int = LOCAL_K,
) -> Dict[str, float]:

    model.eval()

    with torch.no_grad():

        z = model.encode(
            dataset
        )

        d_x = pairwise_distance(
            dataset
        )

        d_z = pairwise_distance(
            z
        )

        neighbors = build_local_neighbors(
            d_x,
            k,
        )

        local_x = torch.gather(
            d_x,
            1,
            neighbors,
        )

        local_z = torch.gather(
            d_z,
            1,
            neighbors,
        )

        # ----------------------------------------------------------
        # Relative local distance error
        # ----------------------------------------------------------

        local_radius = torch.clamp(
            local_x[:, -1:],
            min=EPS,
        )

        normalized_x = (
            local_x
            /
            local_radius
        )

        normalized_z = (
            local_z
            /
            torch.clamp(
                local_z[:, -1:],
                min=EPS,
            )
        )

        relative_error = torch.mean(
            torch.abs(
                normalized_z
                -
                normalized_x
            )
        )

        # ----------------------------------------------------------
        # Local rank accuracy
        # ----------------------------------------------------------

        correct = (
            local_z[:, 1:]
            >=
            local_z[:, :-1]
        )

        valid = (
            local_x[:, 1:]
            >
            local_x[:, :-1]
            +
            1e-6
        )

        if valid.any():

            rank_accuracy = (
                correct[valid]
                .float()
                .mean()
            )

        else:

            rank_accuracy = torch.tensor(
                1.0,
                device=dataset.device,
            )

        # ----------------------------------------------------------
        # Nearest-neighbor preservation
        # ----------------------------------------------------------

        # True nearest structural neighbor.
        true_nn = neighbors[:, 0]

        # In latent space, find nearest neighbor.
        latent_mask = torch.eye(
            dataset.shape[0],
            dtype=torch.bool,
            device=dataset.device,
        )

        d_z_masked = d_z.masked_fill(
            latent_mask,
            float("inf"),
        )

        latent_nn = torch.argmin(
            d_z_masked,
            dim=1,
        )

        nn_recall = (
            latent_nn
            ==
            true_nn
        ).float().mean()

    return {

        "local_relative_error":
            float(relative_error),

        "local_rank_accuracy":
            float(rank_accuracy),

        "nearest_neighbor_recall":
            float(nn_recall),
    }


# ======================================================================
# Main Test Suite
# ======================================================================

def run_tests() -> int:

    total = 0

    passed_count = 0

    def check(
        name: str,
        condition: bool,
    ) -> None:

        nonlocal total
        nonlocal passed_count

        total += 1

        if condition:

            passed_count += 1

            passed(name)

        else:

            failed(name)

    # ==================================================================
    # Header
    # ==================================================================

    print("=" * 68)

    print(
        "Neural Struct3D v1.1"
    )

    print(
        "Local Geometry Refinement Regression Suite"
    )

    print("=" * 68)

    print(
        f"Version: {VERSION}"
    )

    print(
        f"Struct3D Representation: "
        f"v{STRUCT3D_VERSION}"
    )

    print(
        f"Seed: {SEED}"
    )

    print(
        f"Device: {DEVICE}"
    )

    print(
        f"Input dimension: {INPUT_DIM}"
    )

    print(
        f"Latent dimension: {LATENT_DIM}"
    )

    print(
        f"Local K: {LOCAL_K}"
    )

    print(
        f"Local anchors: {LOCAL_ANCHORS}"
    )

    # ==================================================================
    # Base World
    # ==================================================================

    world = make_base_world()

    header(
        "[1] Base World"
    )

    print(
        f"Units: {len(world.units)}"
    )

    print(
        f"Objects: {len(world.objects)}"
    )

    print(
        f"Instances: {len(world.instances)}"
    )

    print(
        f"Relations: {len(world.relations)}"
    )

    check(
        "World Validation",
        (
            len(world.units) == 4
            and
            len(world.objects) == 2
            and
            len(world.instances) == 2
            and
            len(world.relations) == 2
        ),
    )

    # ==================================================================
    # Representation
    # ==================================================================

    header(
        "v4.0 Representation Input"
    )

    representation = \
        structural_representation(
            world
        )

    print(
        json.dumps(
            representation,
            indent=2,
        )
    )

    print(
        f"Representation dimension: "
        f"{len(representation)}"
    )

    check(
        "Representation Dimension Is 23",
        len(representation)
        ==
        INPUT_DIM,
    )

    # ==================================================================
    # Model
    # ==================================================================

    header(
        "Neural Struct3D v1.1 Model"
    )

    seed_everything(SEED)

    model = NeuralStruct3D().to(
        DEVICE
    )

    parameter_count = sum(
        p.numel()
        for p in model.parameters()
    )

    print(
        f"Trainable parameters: "
        f"{parameter_count}"
    )

    check(
        "Model Exists",
        isinstance(
            model,
            NeuralStruct3D,
        ),
    )

    # ==================================================================
    # Forward
    # ==================================================================

    header(
        "Forward Pass"
    )

    x = torch.tensor(
        representation,
        dtype=torch.float32,
    ).unsqueeze(0)

    model.eval()

    with torch.no_grad():

        z, x_hat = model(x)

    print(
        f"Input shape: {tuple(x.shape)}"
    )

    print(
        f"Latent shape: {tuple(z.shape)}"
    )

    print(
        f"Reconstruction shape: "
        f"{tuple(x_hat.shape)}"
    )

    check(
        "Forward Pass",
        (
            tuple(x.shape)
            ==
            (1, INPUT_DIM)

            and

            tuple(z.shape)
            ==
            (1, LATENT_DIM)

            and

            tuple(x_hat.shape)
            ==
            (1, INPUT_DIM)
        ),
    )

    # ==================================================================
    # Dataset
    # ==================================================================

    header(
        "Synthetic Structural Dataset"
    )

    worlds = build_training_worlds(
        TRAIN_SAMPLES
    )

    dataset = worlds_to_tensor(
        worlds
    )

    print(
        f"Dataset shape: "
        f"{tuple(dataset.shape)}"
    )

    check(
        "Dataset Dimension Valid",
        dataset.shape[1]
        ==
        INPUT_DIM,
    )

    check(
        "Dataset Has Multiple Structural States",
        torch.unique(
            dataset,
            dim=0,
        ).shape[0]
        >
        8,
    )

    # ==================================================================
    # Training
    # ==================================================================

    header(
        "Neural Struct3D v1.1 "
        "Local Geometry Refinement"
    )

    seed_everything(SEED)

    model = NeuralStruct3D().to(
        DEVICE
    )

    print(
        "Training configuration:"
    )

    print(
        f"  epochs              = "
        f"{TRAIN_EPOCHS}"
    )

    print(
        f"  learning rate       = "
        f"{LEARNING_RATE}"
    )

    print(
        f"  reconstruction      = "
        f"{LAMBDA_RECON}"
    )

    print(
        f"  global distance     = "
        f"{LAMBDA_DISTANCE}"
    )

    print(
        f"  local geometry      = "
        f"{LAMBDA_LOCAL}"
    )

    print(
        f"  local rank          = "
        f"{LAMBDA_RANK}"
    )

    print(
        f"  monotonic           = "
        f"{LAMBDA_MONOTONIC}"
    )

    print(
        f"  local K             = "
        f"{LOCAL_K}"
    )

    print(
        f"  local anchors       = "
        f"{LOCAL_ANCHORS}"
    )

    print()

    result = train_model(
        model,
        dataset,
    )

    print()

    print(
        f"Initial total loss: "
        f"{result.initial_loss:.10f}"
    )

    print(
        f"Final total loss:   "
        f"{result.final_loss:.10f}"
    )

    print(
        f"Initial reconstruction: "
        f"{result.initial_reconstruction:.10f}"
    )

    print(
        f"Final reconstruction:   "
        f"{result.final_reconstruction:.10f}"
    )

    print(
        f"Initial global distance: "
        f"{result.initial_distance:.10f}"
    )

    print(
        f"Final global distance:   "
        f"{result.final_distance:.10f}"
    )

    print(
        f"Initial local geometry: "
        f"{result.initial_local:.10f}"
    )

    print(
        f"Final local geometry:   "
        f"{result.final_local:.10f}"
    )

    print(
        f"Initial rank: "
        f"{result.initial_rank:.10f}"
    )

    print(
        f"Final rank:   "
        f"{result.final_rank:.10f}"
    )

    print(
        f"Initial monotonic: "
        f"{result.initial_monotonic:.10f}"
    )

    print(
        f"Final monotonic:   "
        f"{result.final_monotonic:.10f}"
    )

    check(
        "Training Loss Decreases",
        result.final_loss
        <
        result.initial_loss,
    )

    check(
        "Global Distance Loss Decreases",
        result.final_distance
        <
        result.initial_distance,
    )

    check(
        "Local Geometry Loss Decreases",
        result.final_local
        <
        result.initial_local,
    )

    check(
        "Local Rank Loss Decreases",
        result.final_rank
        <
        result.initial_rank,
    )

    check(
        "Monotonic Loss Decreases",
        result.final_monotonic
        <
        result.initial_monotonic,
    )

    # ==================================================================
    # Reconstruction
    # ==================================================================

    header(
        "Representation Reconstruction"
    )

    base_error = reconstruction_error(
        model,
        world,
    )

    print(
        f"Base reconstruction MAE: "
        f"{base_error:.10f}"
    )

    check(
        "Base Representation Reconstruction",
        base_error
        <
        RECONSTRUCTION_THRESHOLD,
    )

    # ==================================================================
    # Determinism
    # ==================================================================

    header(
        "Latent Determinism"
    )

    x_base = torch.tensor(
        structural_representation(world),
        dtype=torch.float32,
    ).unsqueeze(0)

    model.eval()

    with torch.no_grad():

        z1 = model.encode(
            x_base
        )

        z2 = model.encode(
            x_base
        )

    deterministic_error = float(
        torch.max(
            torch.abs(
                z1 - z2
            )
        )
    )

    print(
        f"Maximum latent difference: "
        f"{deterministic_error:.12f}"
    )

    check(
        "Latent Encoding Deterministic",
        deterministic_error == 0.0,
    )

    # ==================================================================
    # Invariance
    # ==================================================================

    invariance_tests = [

        (
            "Dictionary Order",
            reorder_world,
        ),

        (
            "Unit Relabeling",
            relabel_units,
        ),

        (
            "Object Relabeling",
            relabel_objects,
        ),

        (
            "Instance Relabeling",
            relabel_instances,
        ),

        (
            "Relation Relabeling",
            relabel_relations,
        ),
    ]

    for name, transform in invariance_tests:

        header(
            f"Neural {name} Invariance"
        )

        transformed = transform(
            world
        )

        d_rep = structural_distance(
            world,
            transformed,
        )

        d_latent = latent_distance(
            model,
            world,
            transformed,
        )

        print(
            f"Representation distance: "
            f"{d_rep:.12f}"
        )

        print(
            f"Latent distance: "
            f"{d_latent:.12f}"
        )

        check(
            f"{name} Representation Invariant",
            d_rep == 0.0,
        )

        check(
            f"{name} Latent Invariant",
            d_latent < 1e-7,
        )

    # ==================================================================
    # Mutations
    # ==================================================================

    mutations = {

        "primitive":
            mutate_primitive,

        "object":
            mutate_object_composition,

        "instance":
            mutate_instance_composition,

        "relation_type":
            mutate_relation_type,

        "relation_confidence":
            mutate_relation_confidence,

        "relation_deletion":
            mutate_relation_deletion,
    }

    mutation_rep_distances = {}

    mutation_latent_distances = {}

    for name, mutation in mutations.items():

        header(
            f"Structural Mutation: {name}"
        )

        mutated = mutation(
            world
        )

        d_rep = structural_distance(
            world,
            mutated,
        )

        d_latent = latent_distance(
            model,
            world,
            mutated,
        )

        mutation_rep_distances[
            name
        ] = d_rep

        mutation_latent_distances[
            name
        ] = d_latent

        print(
            f"Representation distance: "
            f"{d_rep:.12f}"
        )

        print(
            f"Latent distance: "
            f"{d_latent:.12f}"
        )

        check(
            f"{name} Representation Mutation Is Positive",
            d_rep > 0.0,
        )

        check(
            f"{name} Latent Mutation Is Positive",
            d_latent > 1e-6,
        )

    # ==================================================================
    # Canonical Distance
    # ==================================================================

    header(
        "Canonical Structural Distance Preservation"
    )

    errors = []

    for name in mutations:

        mutated = mutations[name](
            world
        )

        d_rep = structural_distance(
            world,
            mutated,
        )

        d_latent = latent_distance(
            model,
            world,
            mutated,
        )

        if d_rep > EPS:

            error = abs(
                d_latent
                -
                d_rep
            ) / d_rep

        else:

            error = 0.0

        errors.append(
            error
        )

        print(
            f"{name:20s} "
            f"R={d_rep:.12f} "
            f"Z={d_latent:.12f} "
            f"relative_error={error:.6f}"
        )

    mean_error = (
        sum(errors)
        /
        max(
            len(errors),
            1,
        )
    )

    print(
        f"Mean relative distance error: "
        f"{mean_error:.6f}"
    )

    check(
        "Latent Space Approximately Preserves Structural Distance",
        mean_error
        <
        DISTANCE_RELATIVE_ERROR_THRESHOLD,
    )

    # ==================================================================
    # v1.1 Local Geometry Evaluation
    # ==================================================================

    header(
        "v1.1 Local Geometry Refinement Evaluation"
    )

    local_metrics = evaluate_local_geometry(
        model,
        dataset,
        LOCAL_K,
    )

    print(
        f"Local normalized distance error: "
        f"{local_metrics['local_relative_error']:.8f}"
    )

    print(
        f"Local rank accuracy: "
        f"{local_metrics['local_rank_accuracy']:.8f}"
    )

    print(
        f"Nearest-neighbor recall: "
        f"{local_metrics['nearest_neighbor_recall']:.8f}"
    )

    check(
        "Local Geometry Error Is Controlled",
        local_metrics[
            "local_relative_error"
        ]
        <
        LOCAL_DISTANCE_RELATIVE_ERROR_THRESHOLD,
    )

    check(
        "Local Rank Accuracy Is Valid",
        local_metrics[
            "local_rank_accuracy"
        ]
        >=
        LOCAL_RANK_ACCURACY_THRESHOLD,
    )

    check(
        "Local Nearest Neighbor Preservation",
        local_metrics[
            "nearest_neighbor_recall"
        ]
        >=
        LOCAL_NEIGHBOR_RECALL_THRESHOLD,
    )

    # ==================================================================
    # Symmetry
    # ==================================================================

    header(
        "Latent Distance Symmetry"
    )

    mutated = mutate_object_composition(
        world
    )

    d_ab = latent_distance(
        model,
        world,
        mutated,
    )

    d_ba = latent_distance(
        model,
        mutated,
        world,
    )

    symmetry_error = abs(
        d_ab
        -
        d_ba
    )

    print(
        f"Z(W,M): {d_ab:.12f}"
    )

    print(
        f"Z(M,W): {d_ba:.12f}"
    )

    print(
        f"Symmetry error: "
        f"{symmetry_error:.12f}"
    )

    check(
        "Latent Distance Symmetry",
        symmetry_error < 1e-7,
    )

    # ==================================================================
    # Collapse
    # ==================================================================

    header(
        "Latent Distance Collapse Analysis"
    )

    model.eval()

    with torch.no_grad():

        z_all = model.encode(
            dataset
        )

    d_x = pairwise_distance(
        dataset
    )

    d_z = pairwise_distance(
        z_all
    )

    mask = torch.triu(
        torch.ones_like(
            d_x,
            dtype=torch.bool,
        ),
        diagonal=1,
    )

    x_values = d_x[mask]

    z_values = d_z[mask]

    mean_x = float(
        x_values.mean()
    )

    mean_z = float(
        z_values.mean()
    )

    std_x = float(
        x_values.std()
    )

    std_z = float(
        z_values.std()
    )

    ratio_mean = (
        mean_z
        /
        max(
            mean_x,
            EPS,
        )
    )

    ratio_std = (
        std_z
        /
        max(
            std_x,
            EPS,
        )
    )

    print(
        f"Representation mean distance: "
        f"{mean_x:.8f}"
    )

    print(
        f"Latent mean distance: "
        f"{mean_z:.8f}"
    )

    print(
        f"Representation distance std: "
        f"{std_x:.8f}"
    )

    print(
        f"Latent distance std: "
        f"{std_z:.8f}"
    )

    print(
        f"Mean distance ratio: "
        f"{ratio_mean:.8f}"
    )

    print(
        f"Std distance ratio: "
        f"{ratio_std:.8f}"
    )

    check(
        "Latent Space Does Not Collapse",
        (
            mean_z > 0.1
            and
            std_z > 0.1
        ),
    )

    # ==================================================================
    # Serialization
    # ==================================================================

    header(
        "Neural Struct3D Serialization"
    )

    state = {
        key: value.detach().cpu()
        for key, value
        in model.state_dict().items()
    }

    serialized = {
        key: value.tolist()
        for key, value
        in state.items()
    }

    payload = json.dumps(
        serialized,
        sort_keys=True,
    )

    print(
        f"Serialized parameter bytes: "
        f"{len(payload.encode('utf-8'))}"
    )

    check(
        "Model State Is JSON Serializable",
        len(payload) > 0,
    )

    # ==================================================================
    # Checkpoint
    # ==================================================================

    header(
        "Checkpoint Save"
    )

    checkpoint_path = os.path.join(

        os.path.dirname(__file__)
        if "__file__" in globals()
        else ".",

        "neural_struct3d_v1_1_checkpoint.pt",
    )

    try:

        torch.save(

            {
                "version":
                    VERSION,

                "struct3d_version":
                    STRUCT3D_VERSION,

                "input_dim":
                    INPUT_DIM,

                "latent_dim":
                    LATENT_DIM,

                "hidden_dim_1":
                    HIDDEN_DIM_1,

                "hidden_dim_2":
                    HIDDEN_DIM_2,

                "lambda_recon":
                    LAMBDA_RECON,

                "lambda_distance":
                    LAMBDA_DISTANCE,

                "lambda_local":
                    LAMBDA_LOCAL,

                "lambda_rank":
                    LAMBDA_RANK,

                "lambda_monotonic":
                    LAMBDA_MONOTONIC,

                "lambda_latent":
                    LAMBDA_LATENT,

                "local_k":
                    LOCAL_K,

                "local_anchors":
                    LOCAL_ANCHORS,

                "rank_margin":
                    RANK_MARGIN,

                "seed":
                    SEED,

                "state_dict":
                    model.state_dict(),
            },

            checkpoint_path,
        )

        print(
            f"Checkpoint: "
            f"{checkpoint_path}"
        )

        check(
            "Checkpoint Saved",
            os.path.exists(
                checkpoint_path
            ),
        )

    except Exception as exc:

        print(
            f"Checkpoint save error: "
            f"{exc}"
        )

        check(
            "Checkpoint Saved",
            False,
        )

    # ==================================================================
    # Reload
    # ==================================================================

    header(
        "Checkpoint Reload"
    )

    try:

        loaded = torch.load(
            checkpoint_path,
            map_location=DEVICE,
            weights_only=True,
        )

        reloaded_model = \
            NeuralStruct3D().to(
                DEVICE
            )

        reloaded_model.load_state_dict(
            loaded["state_dict"]
        )

        reloaded_model.eval()

        with torch.no_grad():

            z_original = model.encode(
                x_base
            )

            z_reload = \
                reloaded_model.encode(
                    x_base
                )

        reload_error = float(
            torch.max(
                torch.abs(
                    z_original
                    -
                    z_reload
                )
            )
        )

        print(
            f"Reload latent max error: "
            f"{reload_error:.12f}"
        )

        check(
            "Checkpoint Reload Preserves Encoder",
            reload_error < 1e-7,
        )

    except Exception as exc:

        print(
            f"Reload error: {exc}"
        )

        check(
            "Checkpoint Reload Preserves Encoder",
            False,
        )

    # ==================================================================
    # API
    # ==================================================================

    header(
        "Neural Struct3D v1.1 Compatibility"
    )

    api_output = {

        "version":
            VERSION,

        "struct3d_version":
            STRUCT3D_VERSION,

        "input_dim":
            INPUT_DIM,

        "latent_dim":
            LATENT_DIM,

        "local_geometry":
            {

                "local_k":
                    LOCAL_K,

                "local_anchors":
                    LOCAL_ANCHORS,

                "objective":
                    "local_normalized_distance_preservation",
            },

        "loss":
            {

                "reconstruction":
                    LAMBDA_RECON,

                "distance":
                    LAMBDA_DISTANCE,

                "local_geometry":
                    LAMBDA_LOCAL,

                "rank":
                    LAMBDA_RANK,

                "monotonic":
                    LAMBDA_MONOTONIC,

                "latent_regularization":
                    LAMBDA_LATENT,
            },

        "rank_margin":
            RANK_MARGIN,

        "encoder":
            {

                "input_dim":
                    INPUT_DIM,

                "latent_dim":
                    LATENT_DIM,
            },

        "decoder":
            {

                "latent_dim":
                    LATENT_DIM,

                "output_dim":
                    INPUT_DIM,
            },

        "representation_hash":
            representation_hash(
                world
            ),
    }

    print(
        json.dumps(
            api_output,
            indent=2,
        )
    )

    api_json = json.dumps(
        api_output,
        sort_keys=True,
    )

    check(
        "Neural Struct3D Target Is Serializable",
        len(api_json) > 0,
    )

    # ==================================================================
    # Final
    # ==================================================================

    print()

    print("=" * 68)

    print(
        "Neural Struct3D v1.1"
    )

    print("=" * 68)

    print(
        f"Total tests: "
        f"{total}"
    )

    print(
        f"Passed: "
        f"{passed_count}"
    )

    print(
        f"Failed: "
        f"{total - passed_count}"
    )

    if passed_count == total:

        print(
            "STATUS: PASS"
        )

    else:

        print(
            "STATUS: FAIL"
        )

    print("=" * 68)

    return (
        0
        if passed_count == total
        else 1
    )


# ======================================================================
# Main
# ======================================================================

if __name__ == "__main__":

    seed_everything(SEED)

    sys.exit(
        run_tests()
    )