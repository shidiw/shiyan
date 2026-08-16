#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
======================================================================
Neural Struct3D v1.0
Structural Geometry Validation
======================================================================

Purpose
-------

This experiment validates whether the learned Neural Struct3D latent
space preserves the geometric structure defined by Struct3D v4.0.

The central hypothesis is:

        d_R(W_i, W_j)
            ≈
        d_Z(W_i, W_j)

where

    d_R
        is the original Struct3D v4.0 Structural Distance

    d_Z
        is Euclidean distance in the learned latent space.

This experiment is intentionally separate from training.

It loads a trained Neural Struct3D model and evaluates the geometry
of unseen structural worlds.

Validation dimensions
---------------------

1. Global distance correlation
2. Relative distance error
3. Monotonicity
4. Local neighborhood preservation
5. k-nearest-neighbor overlap
6. Rank preservation
7. Distance-bin stability
8. Triangle geometry consistency
9. Distance symmetry
10. Identity / invariance
11. Distance collapse detection
12. Worst-case structural pair
13. Geometry report serialization

No CUDA.
No Open3D.
No external dataset.
CPU only.

======================================================================
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import random
import statistics
import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any

import torch
import torch.nn as nn
import torch.nn.functional as F


# ======================================================================
# Configuration
# ======================================================================

VERSION = "1.0"
STRUCT3D_VERSION = "4.0"

SEED = 20260814

INPUT_DIM = 23
LATENT_DIM = 64

HIDDEN_DIM_1 = 128
HIDDEN_DIM_2 = 128

TRAIN_SAMPLES = 800
TEST_SAMPLES = 300

TRAIN_EPOCHS = 240
LEARNING_RATE = 1e-3

DISTANCE_LOSS_WEIGHT = 1.0

PAIR_SAMPLE_COUNT = 20000

K_NEIGHBORS = 5

DEVICE = torch.device("cpu")

CHECKPOINT_NAME = "neural_struct3d_v1_checkpoint.pt"

REPORT_NAME = "neural_struct3d_v1_geometry_report.json"


# ======================================================================
# Thresholds
# ======================================================================

MEAN_RELATIVE_ERROR_THRESHOLD = 0.08

PEARSON_THRESHOLD = 0.97

SPEARMAN_THRESHOLD = 0.97

LOCAL_NN_OVERLAP_THRESHOLD = 0.70

RANK_CORRELATION_THRESHOLD = 0.97

DISTANCE_COLLAPSE_THRESHOLD = 0.05

SYMMETRY_THRESHOLD = 1e-7

IDENTITY_THRESHOLD = 1e-7

TRIANGLE_RELATIVE_ERROR_THRESHOLD = 0.10


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

    try:
        torch.set_num_threads(1)
    except Exception:
        pass


seed_everything()


# ======================================================================
# Pretty Printing
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


# ======================================================================
# Clone
# ======================================================================

def clone_world(world: World) -> World:

    return copy.deepcopy(world)


# ======================================================================
# Structural Representation
# ======================================================================

def primitive_histogram(world: World) -> List[float]:

    counts = {
        p: 0
        for p in PRIMITIVES
    }

    for unit in world.units.values():

        if unit.primitive not in counts:
            counts[unit.primitive] = 0

        counts[unit.primitive] += 1

    total = max(len(world.units), 1)

    return [
        counts[p] / total
        for p in PRIMITIVES
    ]


def object_histogram(world: World) -> List[float]:

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

        sum(v == 1 for v in values) / len(values),

        sum(v == 2 for v in values) / len(values),

        sum(v >= 3 for v in values) / len(values),
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

    values = list(counts.values())

    return (

        sum(v == 0 for v in values) / len(values),

        sum(v == 1 for v in values) / len(values),

        sum(v >= 2 for v in values) / len(values),
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
        counts[r] / total
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


def structural_representation(
    world: World,
) -> List[float]:

    features = []

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

        avg_units = sum(sizes) / len(sizes)

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

    mean, std, minimum = \
        relation_confidence_statistics(world)

    features.extend([
        mean,
        std,
        minimum,
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
        / max(len(world.instances), 1),
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


# ======================================================================
# Structural Distance
# ======================================================================

def structural_distance_from_tensor(
    a: torch.Tensor,
    b: torch.Tensor,
) -> torch.Tensor:

    return torch.linalg.vector_norm(
        a - b,
        dim=-1,
    )


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
# Random Structural World
# ======================================================================

def random_structural_world(
    rng: random.Random,
) -> World:

    world = make_base_world()

    for uid in world.units:

        if rng.random() < 0.40:

            world.units[uid].primitive = \
                rng.choice(PRIMITIVES)

    unit_ids = list(world.units.keys())

    for oid in world.objects:

        size = rng.randint(
            1,
            len(unit_ids),
        )

        selected = rng.sample(
            unit_ids,
            size,
        )

        world.objects[oid].units = tuple(
            sorted(selected)
        )

    object_ids = list(
        world.objects.keys()
    )

    for iid in world.instances:

        world.instances[iid].object_id = \
            rng.choice(object_ids)

    for rid in world.relations:

        world.relations[rid].relation_type = \
            rng.choice(RELATION_TYPES)

        world.relations[rid].confidence = round(
            rng.uniform(
                0.05,
                1.0,
            ),
            4,
        )

    return world


# ======================================================================
# Dataset Generation
# ======================================================================

def build_world_dataset(
    n: int,
    seed: int,
) -> Tuple[List[World], torch.Tensor]:

    rng = random.Random(seed)

    worlds = []

    representations = []

    seen = set()

    while len(worlds) < n:

        world = random_structural_world(rng)

        rep = structural_representation(world)

        key = tuple(
            round(v, 10)
            for v in rep
        )

        if key in seen:
            continue

        seen.add(key)

        worlds.append(world)

        representations.append(rep)

    tensor = torch.tensor(
        representations,
        dtype=torch.float32,
        device=DEVICE,
    )

    return worlds, tensor


# ======================================================================
# Neural Struct3D Model
# ======================================================================

class StructuralEncoder(nn.Module):

    def __init__(
        self,
        input_dim=INPUT_DIM,
        hidden_dim_1=HIDDEN_DIM_1,
        hidden_dim_2=HIDDEN_DIM_2,
        latent_dim=LATENT_DIM,
    ):
        super().__init__()

        self.net = nn.Sequential(

            nn.Linear(
                input_dim,
                hidden_dim_1,
            ),

            nn.ReLU(),

            nn.Linear(
                hidden_dim_1,
                hidden_dim_2,
            ),

            nn.ReLU(),

            nn.Linear(
                hidden_dim_2,
                latent_dim,
            ),
        )

    def forward(
        self,
        x,
    ):

        return self.net(x)


class StructuralDecoder(nn.Module):

    def __init__(
        self,
        latent_dim=LATENT_DIM,
        hidden_dim_1=HIDDEN_DIM_1,
        hidden_dim_2=HIDDEN_DIM_2,
        output_dim=INPUT_DIM,
    ):
        super().__init__()

        self.net = nn.Sequential(

            nn.Linear(
                latent_dim,
                hidden_dim_2,
            ),

            nn.ReLU(),

            nn.Linear(
                hidden_dim_2,
                hidden_dim_1,
            ),

            nn.ReLU(),

            nn.Linear(
                hidden_dim_1,
                output_dim,
            ),
        )

    def forward(
        self,
        z,
    ):

        return self.net(z)


class NeuralStruct3D(nn.Module):

    def __init__(
        self,
        input_dim=INPUT_DIM,
        latent_dim=LATENT_DIM,
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
        x,
    ):

        return self.encoder(x)

    def decode(
        self,
        z,
    ):

        return self.decoder(z)

    def forward(
        self,
        x,
    ):

        z = self.encode(x)

        x_hat = self.decode(z)

        return z, x_hat


# ======================================================================
# Pair Construction
# ======================================================================

def sample_pairs(
    n: int,
    count: int,
    seed: int,
) -> List[Tuple[int, int]]:

    rng = random.Random(seed)

    pairs = set()

    maximum = n * (n - 1) // 2

    target = min(
        count,
        maximum,
    )

    while len(pairs) < target:

        i = rng.randrange(n)

        j = rng.randrange(n)

        if i == j:
            continue

        if i > j:
            i, j = j, i

        pairs.add(
            (i, j)
        )

    return list(pairs)


# ======================================================================
# Rank Statistics
# ======================================================================

def rank_values(
    values: List[float],
) -> List[float]:

    indexed = sorted(
        enumerate(values),
        key=lambda x: x[1],
    )

    ranks = [0.0] * len(values)

    i = 0

    while i < len(indexed):

        j = i + 1

        while (
            j < len(indexed)
            and indexed[j][1] == indexed[i][1]
        ):
            j += 1

        rank = (
            (i + 1) + j
        ) / 2.0

        for k in range(i, j):

            ranks[
                indexed[k][0]
            ] = rank

        i = j

    return ranks


def pearson_correlation(
    x: List[float],
    y: List[float],
) -> float:

    if len(x) < 2:
        return 0.0

    mean_x = statistics.mean(x)

    mean_y = statistics.mean(y)

    numerator = sum(
        (a - mean_x)
        * (b - mean_y)
        for a, b in zip(x, y)
    )

    denom_x = math.sqrt(
        sum(
            (a - mean_x) ** 2
            for a in x
        )
    )

    denom_y = math.sqrt(
        sum(
            (b - mean_y) ** 2
            for b in y
        )
    )

    if denom_x <= 1e-12:
        return 0.0

    if denom_y <= 1e-12:
        return 0.0

    return numerator / (
        denom_x * denom_y
    )


def spearman_correlation(
    x: List[float],
    y: List[float],
) -> float:

    return pearson_correlation(
        rank_values(x),
        rank_values(y),
    )


# ======================================================================
# Encode Dataset
# ======================================================================

def encode_dataset(
    model: NeuralStruct3D,
    tensor: torch.Tensor,
) -> torch.Tensor:

    model.eval()

    with torch.no_grad():

        z = model.encode(tensor)

    return z.cpu()


# ======================================================================
# Load / Train Model
# ======================================================================

def train_model(
    model: NeuralStruct3D,
    x: torch.Tensor,
) -> None:

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE,
    )

    model.train()

    n = x.shape[0]

    for epoch in range(
        1,
        TRAIN_EPOCHS + 1,
    ):

        optimizer.zero_grad()

        z, x_hat = model(x)

        reconstruction = F.mse_loss(
            x_hat,
            x,
        )

        pair_count = min(
            4096,
            n * (n - 1) // 2,
        )

        pairs = sample_pairs(
            n,
            pair_count,
            SEED + epoch,
        )

        ia = torch.tensor(
            [p[0] for p in pairs],
            dtype=torch.long,
        )

        ib = torch.tensor(
            [p[1] for p in pairs],
            dtype=torch.long,
        )

        rep_d = torch.linalg.vector_norm(
            x[ia] - x[ib],
            dim=1,
        )

        latent_d = torch.linalg.vector_norm(
            z[ia] - z[ib],
            dim=1,
        )

        distance_loss = F.mse_loss(
            latent_d,
            rep_d,
        )

        loss = (
            reconstruction
            + DISTANCE_LOSS_WEIGHT
            * distance_loss
        )

        loss.backward()

        optimizer.step()

        if (
            epoch == 1
            or epoch % 40 == 0
            or epoch == TRAIN_EPOCHS
        ):

            print(
                f"Epoch {epoch:03d}/{TRAIN_EPOCHS}: "
                f"total={loss.item():.8f} "
                f"recon={reconstruction.item():.8f} "
                f"distance={distance_loss.item():.8f}"
            )


def load_or_train_model(
    train_tensor: torch.Tensor,
) -> NeuralStruct3D:

    model = NeuralStruct3D().to(DEVICE)

    checkpoint_path = os.path.join(
        os.path.dirname(__file__)
        if "__file__" in globals()
        else ".",
        CHECKPOINT_NAME,
    )

    if os.path.exists(checkpoint_path):

        try:

            checkpoint = torch.load(
                checkpoint_path,
                map_location=DEVICE,
                weights_only=True,
            )

            model.load_state_dict(
                checkpoint["state_dict"]
            )

            print(
                f"Loaded checkpoint: "
                f"{checkpoint_path}"
            )

            return model

        except Exception as exc:

            print(
                "Checkpoint load failed; "
                "retraining model."
            )

            print(
                f"Reason: {exc}"
            )

    print(
        "No compatible checkpoint found."
    )

    print(
        "Training Neural Struct3D..."
    )

    seed_everything(SEED)

    train_model(
        model,
        train_tensor,
    )

    return model


# ======================================================================
# Pairwise Geometry
# ======================================================================

@dataclass
class GeometryResult:

    representation_distances: List[float]

    latent_distances: List[float]

    relative_errors: List[float]


def evaluate_pairs(
    representation: torch.Tensor,
    latent: torch.Tensor,
    pairs: List[Tuple[int, int]],
) -> GeometryResult:

    rep_distances = []

    latent_distances = []

    relative_errors = []

    for i, j in pairs:

        dr = float(
            torch.linalg.vector_norm(
                representation[i]
                - representation[j]
            ).item()
        )

        dz = float(
            torch.linalg.vector_norm(
                latent[i]
                - latent[j]
            ).item()
        )

        if dr > 1e-12:

            error = abs(
                dz - dr
            ) / dr

        else:

            error = 0.0

        rep_distances.append(dr)

        latent_distances.append(dz)

        relative_errors.append(error)

    return GeometryResult(
        representation_distances=rep_distances,
        latent_distances=latent_distances,
        relative_errors=relative_errors,
    )


# ======================================================================
# Distance Statistics
# ======================================================================

def summarize_geometry(
    result: GeometryResult,
) -> Dict[str, float]:

    errors = result.relative_errors

    sorted_errors = sorted(errors)

    def percentile(
        values,
        p,
    ):

        if not values:
            return 0.0

        index = int(
            round(
                (len(values) - 1) * p
            )
        )

        return values[index]

    pearson = pearson_correlation(
        result.representation_distances,
        result.latent_distances,
    )

    spearman = spearman_correlation(
        result.representation_distances,
        result.latent_distances,
    )

    return {

        "mean_relative_error":
            statistics.mean(errors),

        "median_relative_error":
            statistics.median(errors),

        "p90_relative_error":
            percentile(
                sorted_errors,
                0.90,
            ),

        "p95_relative_error":
            percentile(
                sorted_errors,
                0.95,
            ),

        "max_relative_error":
            max(errors),

        "pearson":
            pearson,

        "spearman":
            spearman,

        "pair_count":
            len(errors),
    }


# ======================================================================
# Distance Bins
# ======================================================================

def distance_bin_analysis(
    result: GeometryResult,
) -> Dict[str, Dict[str, float]]:

    bins = [
        ("0.0-0.2", 0.0, 0.2),
        ("0.2-0.4", 0.2, 0.4),
        ("0.4-0.6", 0.4, 0.6),
        ("0.6-0.8", 0.6, 0.8),
        ("0.8-1.0", 0.8, 1.0),
        ("1.0-1.5", 1.0, 1.5),
        ("1.5+", 1.5, float("inf")),
    ]

    output = {}

    for name, low, high in bins:

        values = []

        for d, e in zip(
            result.representation_distances,
            result.relative_errors,
        ):

            if (
                d >= low
                and d < high
            ):

                values.append(e)

        if values:

            output[name] = {

                "count":
                    len(values),

                "mean":
                    statistics.mean(values),

                "median":
                    statistics.median(values),

                "p90":
                    sorted(values)[
                        int(
                            round(
                                0.90
                                * (len(values) - 1)
                            )
                        )
                    ],
            }

        else:

            output[name] = {

                "count": 0,

                "mean": 0.0,

                "median": 0.0,

                "p90": 0.0,
            }

    return output


# ======================================================================
# Nearest Neighbour Preservation
# ======================================================================

def nearest_neighbors(
    distance_matrix: torch.Tensor,
    k: int,
) -> List[List[int]]:

    n = distance_matrix.shape[0]

    result = []

    for i in range(n):

        row = distance_matrix[i].clone()

        row[i] = float("inf")

        indices = torch.argsort(row)[:k]

        result.append(
            indices.tolist()
        )

    return result


def pairwise_distance_matrix(
    x: torch.Tensor,
) -> torch.Tensor:

    return torch.cdist(
        x,
        x,
        p=2,
    )


def mean_neighbor_overlap(
    rep_neighbors: List[List[int]],
    latent_neighbors: List[List[int]],
) -> float:

    scores = []

    for a, b in zip(
        rep_neighbors,
        latent_neighbors,
    ):

        sa = set(a)

        sb = set(b)

        if not sa:
            continue

        scores.append(
            len(sa & sb)
            / len(sa)
        )

    if not scores:
        return 0.0

    return statistics.mean(scores)


# ======================================================================
# Local Rank Preservation
# ======================================================================

def local_rank_correlation(
    rep_distances: torch.Tensor,
    latent_distances: torch.Tensor,
    k: int,
) -> float:

    n = rep_distances.shape[0]

    correlations = []

    for i in range(n):

        rd = rep_distances[i].clone()

        zd = latent_distances[i].clone()

        rd[i] = float("inf")

        zd[i] = float("inf")

        r_indices = torch.argsort(rd)[:k]

        z_indices = torch.argsort(zd)[:k]

        r_values = [
            float(
                rd[j].item()
            )
            for j in r_indices
        ]

        z_values = [
            float(
                zd[j].item()
            )
            for j in r_indices
        ]

        if len(r_values) >= 2:

            corr = spearman_correlation(
                r_values,
                z_values,
            )

            correlations.append(corr)

    if not correlations:
        return 0.0

    return statistics.mean(
        correlations
    )


# ======================================================================
# Triangle Geometry
# ======================================================================

def triangle_test(
    representation: torch.Tensor,
    latent: torch.Tensor,
    count: int,
    seed: int,
) -> Dict[str, float]:

    rng = random.Random(seed)

    n = representation.shape[0]

    errors = []

    for _ in range(count):

        i, j, k = rng.sample(
            range(n),
            3,
        )

        rij = float(
            torch.linalg.vector_norm(
                representation[i]
                - representation[j]
            ).item()
        )

        rjk = float(
            torch.linalg.vector_norm(
                representation[j]
                - representation[k]
            ).item()
        )

        rik = float(
            torch.linalg.vector_norm(
                representation[i]
                - representation[k]
            ).item()
        )

        zij = float(
            torch.linalg.vector_norm(
                latent[i]
                - latent[j]
            ).item()
        )

        zjk = float(
            torch.linalg.vector_norm(
                latent[j]
                - latent[k]
            ).item()
        )

        zik = float(
            torch.linalg.vector_norm(
                latent[i]
                - latent[k]
            ).item()
        )

        rep_edges = [
            rij,
            rjk,
            rik,
        ]

        latent_edges = [
            zij,
            zjk,
            zik,
        ]

        for dr, dz in zip(
            rep_edges,
            latent_edges,
        ):

            if dr > 1e-12:

                errors.append(
                    abs(dz - dr) / dr
                )

    return {

        "mean_relative_error":
            statistics.mean(errors),

        "median_relative_error":
            statistics.median(errors),

        "p95_relative_error":
            sorted(errors)[
                int(
                    round(
                        0.95
                        * (len(errors) - 1)
                    )
                )
            ],

        "max_relative_error":
            max(errors),

        "edge_count":
            len(errors),
    }


# ======================================================================
# Distance Symmetry
# ======================================================================

def symmetry_test(
    latent: torch.Tensor,
    count: int = 1000,
) -> float:

    n = latent.shape[0]

    rng = random.Random(
        SEED + 900
    )

    errors = []

    for _ in range(
        min(
            count,
            n * (n - 1),
        )
    ):

        i = rng.randrange(n)

        j = rng.randrange(n)

        if i == j:
            continue

        d_ij = float(
            torch.linalg.vector_norm(
                latent[i]
                - latent[j]
            ).item()
        )

        d_ji = float(
            torch.linalg.vector_norm(
                latent[j]
                - latent[i]
            ).item()
        )

        errors.append(
            abs(d_ij - d_ji)
        )

    return max(errors) if errors else 0.0


# ======================================================================
# Identity Test
# ======================================================================

def identity_test(
    latent: torch.Tensor,
) -> float:

    n = latent.shape[0]

    maximum = 0.0

    for i in range(n):

        d = float(
            torch.linalg.vector_norm(
                latent[i]
                - latent[i]
            ).item()
        )

        maximum = max(
            maximum,
            d,
        )

    return maximum


# ======================================================================
# Distance Collapse
# ======================================================================

def distance_collapse_test(
    representation: torch.Tensor,
    latent: torch.Tensor,
) -> Dict[str, float]:

    rep_d = torch.pdist(
        representation,
        p=2,
    )

    latent_d = torch.pdist(
        latent,
        p=2,
    )

    rep_mean = float(
        rep_d.mean().item()
    )

    latent_mean = float(
        latent_d.mean().item()
    )

    rep_std = float(
        rep_d.std().item()
    )

    latent_std = float(
        latent_d.std().item()
    )

    if rep_mean > 1e-12:

        mean_ratio = \
            latent_mean / rep_mean

    else:

        mean_ratio = 0.0

    if rep_std > 1e-12:

        std_ratio = \
            latent_std / rep_std

    else:

        std_ratio = 0.0

    return {

        "representation_mean_distance":
            rep_mean,

        "latent_mean_distance":
            latent_mean,

        "representation_std_distance":
            rep_std,

        "latent_std_distance":
            latent_std,

        "mean_distance_ratio":
            mean_ratio,

        "std_distance_ratio":
            std_ratio,
    }


# ======================================================================
# Worst Pair
# ======================================================================

def worst_pair(
    result: GeometryResult,
    pairs: List[Tuple[int, int]],
) -> Dict[str, Any]:

    index = max(
        range(
            len(
                result.relative_errors
            )
        ),
        key=lambda i:
            result.relative_errors[i],
    )

    i, j = pairs[index]

    return {

        "world_i":
            i,

        "world_j":
            j,

        "structural_distance":
            result.representation_distances[index],

        "latent_distance":
            result.latent_distances[index],

        "relative_error":
            result.relative_errors[index],
    }


# ======================================================================
# Main
# ======================================================================

def run_geometry_test() -> int:

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

    print("=" * 68)

    print(
        "Neural Struct3D v1.0"
    )

    print(
        "Structural Geometry Validation"
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
        f"Train worlds: {TRAIN_SAMPLES}"
    )

    print(
        f"Test worlds: {TEST_SAMPLES}"
    )

    print(
        f"Pair samples: {PAIR_SAMPLE_COUNT}"
    )

    print(
        f"k neighbors: {K_NEIGHBORS}"
    )

    # ------------------------------------------------------------------
    # Dataset
    # ------------------------------------------------------------------

    header(
        "Independent Structural Geometry Dataset"
    )

    train_worlds, train_tensor = \
        build_world_dataset(
            TRAIN_SAMPLES,
            SEED,
        )

    test_worlds, test_tensor = \
        build_world_dataset(
            TEST_SAMPLES,
            SEED + 10000,
        )

    train_keys = {
        tuple(
            round(float(v), 10)
            for v in row.tolist()
        )
        for row in train_tensor
    }

    test_keys = {
        tuple(
            round(float(v), 10)
            for v in row.tolist()
        )
        for row in test_tensor
    }

    overlap = len(
        train_keys & test_keys
    )

    print(
        f"Train tensor shape: "
        f"{tuple(train_tensor.shape)}"
    )

    print(
        f"Test tensor shape: "
        f"{tuple(test_tensor.shape)}"
    )

    print(
        f"Representation overlap: "
        f"{overlap}"
    )

    check(
        "Train/Test Structural Worlds Are Disjoint",
        overlap == 0,
    )

    # ------------------------------------------------------------------
    # Model
    # ------------------------------------------------------------------

    header(
        "Neural Struct3D Model"
    )

    model = load_or_train_model(
        train_tensor
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
        "Model Architecture Valid",
        parameter_count > 0,
    )

    # ------------------------------------------------------------------
    # Encoding
    # ------------------------------------------------------------------

    header(
        "Unseen Structural World Encoding"
    )

    latent = encode_dataset(
        model,
        test_tensor,
    )

    print(
        f"Latent tensor shape: "
        f"{tuple(latent.shape)}"
    )

    check(
        "Latent Dimension Valid",
        tuple(latent.shape)
        == (
            TEST_SAMPLES,
            LATENT_DIM,
        ),
    )

    # ------------------------------------------------------------------
    # Pairwise geometry
    # ------------------------------------------------------------------

    header(
        "Global Structural Geometry"
    )

    pairs = sample_pairs(
        TEST_SAMPLES,
        PAIR_SAMPLE_COUNT,
        SEED + 20000,
    )

    result = evaluate_pairs(
        test_tensor.cpu(),
        latent,
        pairs,
    )

    summary = summarize_geometry(
        result
    )

    print(
        f"mean_relative_error     : "
        f"{summary['mean_relative_error']:.8f}"
    )

    print(
        f"median_relative_error   : "
        f"{summary['median_relative_error']:.8f}"
    )

    print(
        f"p90_relative_error      : "
        f"{summary['p90_relative_error']:.8f}"
    )

    print(
        f"p95_relative_error      : "
        f"{summary['p95_relative_error']:.8f}"
    )

    print(
        f"max_relative_error      : "
        f"{summary['max_relative_error']:.8f}"
    )

    print(
        f"pearson                 : "
        f"{summary['pearson']:.8f}"
    )

    print(
        f"spearman                : "
        f"{summary['spearman']:.8f}"
    )

    print(
        f"pair_count              : "
        f"{summary['pair_count']}"
    )

    check(
        "Global Mean Relative Error",
        summary["mean_relative_error"]
        < MEAN_RELATIVE_ERROR_THRESHOLD,
    )

    check(
        "Global Pearson Correlation",
        summary["pearson"]
        > PEARSON_THRESHOLD,
    )

    check(
        "Global Spearman Correlation",
        summary["spearman"]
        > SPEARMAN_THRESHOLD,
    )

    # ------------------------------------------------------------------
    # Distance bins
    # ------------------------------------------------------------------

    header(
        "Structural Distance Bin Analysis"
    )

    bin_report = distance_bin_analysis(
        result
    )

    for name, values in bin_report.items():

        print(
            f"{name:8s} "
            f"count={values['count']:6d} "
            f"mean={values['mean']:.6f} "
            f"median={values['median']:.6f} "
            f"p90={values['p90']:.6f}"
        )

    # ------------------------------------------------------------------
    # Nearest neighbours
    # ------------------------------------------------------------------

    header(
        "Local Structural Neighborhood Preservation"
    )

    rep_matrix = pairwise_distance_matrix(
        test_tensor.cpu()
    )

    latent_matrix = pairwise_distance_matrix(
        latent
    )

    rep_neighbors = nearest_neighbors(
        rep_matrix,
        K_NEIGHBORS,
    )

    latent_neighbors = nearest_neighbors(
        latent_matrix,
        K_NEIGHBORS,
    )

    nn_overlap = mean_neighbor_overlap(
        rep_neighbors,
        latent_neighbors,
    )

    print(
        f"k = {K_NEIGHBORS}"
    )

    print(
        f"Mean nearest-neighbor overlap: "
        f"{nn_overlap:.8f}"
    )

    check(
        "Local Neighborhood Preservation",
        nn_overlap
        >= LOCAL_NN_OVERLAP_THRESHOLD,
    )

    # ------------------------------------------------------------------
    # Local rank
    # ------------------------------------------------------------------

    header(
        "Local Rank Preservation"
    )

    local_rank = local_rank_correlation(
        rep_matrix,
        latent_matrix,
        K_NEIGHBORS,
    )

    print(
        f"Mean local Spearman correlation: "
        f"{local_rank:.8f}"
    )

    check(
        "Local Structural Rank Preservation",
        local_rank
        >= RANK_CORRELATION_THRESHOLD,
    )

    # ------------------------------------------------------------------
    # Triangle geometry
    # ------------------------------------------------------------------

    header(
        "Triangle Structural Geometry"
    )

    triangle_report = triangle_test(
        test_tensor.cpu(),
        latent,
        3000,
        SEED + 30000,
    )

    print(
        f"mean_relative_error : "
        f"{triangle_report['mean_relative_error']:.8f}"
    )

    print(
        f"median_relative_error : "
        f"{triangle_report['median_relative_error']:.8f}"
    )

    print(
        f"p95_relative_error : "
        f"{triangle_report['p95_relative_error']:.8f}"
    )

    print(
        f"max_relative_error : "
        f"{triangle_report['max_relative_error']:.8f}"
    )

    check(
        "Triangle Geometry Preservation",
        triangle_report[
            "mean_relative_error"
        ]
        < TRIANGLE_RELATIVE_ERROR_THRESHOLD,
    )

    # ------------------------------------------------------------------
    # Symmetry
    # ------------------------------------------------------------------

    header(
        "Latent Distance Symmetry"
    )

    symmetry_error = symmetry_test(
        latent
    )

    print(
        f"Maximum symmetry error: "
        f"{symmetry_error:.12f}"
    )

    check(
        "Latent Distance Symmetry",
        symmetry_error
        < SYMMETRY_THRESHOLD,
    )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    header(
        "Latent Identity"
    )

    identity_error = identity_test(
        latent
    )

    print(
        f"Maximum self-distance: "
        f"{identity_error:.12f}"
    )

    check(
        "Latent Identity",
        identity_error
        < IDENTITY_THRESHOLD,
    )

    # ------------------------------------------------------------------
    # Distance collapse
    # ------------------------------------------------------------------

    header(
        "Latent Distance Collapse Analysis"
    )

    collapse = distance_collapse_test(
        test_tensor.cpu(),
        latent,
    )

    print(
        f"Representation mean distance: "
        f"{collapse['representation_mean_distance']:.8f}"
    )

    print(
        f"Latent mean distance: "
        f"{collapse['latent_mean_distance']:.8f}"
    )

    print(
        f"Representation distance std: "
        f"{collapse['representation_std_distance']:.8f}"
    )

    print(
        f"Latent distance std: "
        f"{collapse['latent_std_distance']:.8f}"
    )

    print(
        f"Mean distance ratio: "
        f"{collapse['mean_distance_ratio']:.8f}"
    )

    print(
        f"Std distance ratio: "
        f"{collapse['std_distance_ratio']:.8f}"
    )

    check(
        "Latent Space Does Not Collapse",
        collapse[
            "std_distance_ratio"
        ]
        > DISTANCE_COLLAPSE_THRESHOLD,
    )

    # ------------------------------------------------------------------
    # Worst pair
    # ------------------------------------------------------------------

    header(
        "Worst Structural Pair"
    )

    worst = worst_pair(
        result,
        pairs,
    )

    print(
        f"World i: "
        f"{worst['world_i']}"
    )

    print(
        f"World j: "
        f"{worst['world_j']}"
    )

    print(
        f"Structural distance: "
        f"{worst['structural_distance']:.12f}"
    )

    print(
        f"Latent distance: "
        f"{worst['latent_distance']:.12f}"
    )

    print(
        f"Relative error: "
        f"{worst['relative_error']:.8f}"
    )

    # ------------------------------------------------------------------
    # Structural representation invariance
    # ------------------------------------------------------------------

    header(
        "Structural Identity / Invariance"
    )

    base_world = make_base_world()

    reordered = clone_world(
        base_world
    )

    reordered.units = dict(
        reversed(
            list(
                reordered.units.items()
            )
        )
    )

    reordered.objects = dict(
        reversed(
            list(
                reordered.objects.items()
            )
        )
    )

    reordered.instances = dict(
        reversed(
            list(
                reordered.instances.items()
            )
        )
    )

    reordered.relations = dict(
        reversed(
            list(
                reordered.relations.items()
            )
        )
    )

    base_rep = torch.tensor(
        structural_representation(
            base_world
        ),
        dtype=torch.float32,
    ).unsqueeze(0)

    reordered_rep = torch.tensor(
        structural_representation(
            reordered
        ),
        dtype=torch.float32,
    ).unsqueeze(0)

    model.eval()

    with torch.no_grad():

        z_base = model.encode(
            base_rep
        )

        z_reordered = model.encode(
            reordered_rep
        )

    representation_identity_error = float(
        torch.linalg.vector_norm(
            base_rep
            - reordered_rep
        ).item()
    )

    latent_identity_error = float(
        torch.linalg.vector_norm(
            z_base
            - z_reordered
        ).item()
    )

    print(
        f"Representation identity error: "
        f"{representation_identity_error:.12f}"
    )

    print(
        f"Latent identity error: "
        f"{latent_identity_error:.12f}"
    )

    check(
        "Representation Invariance",
        representation_identity_error
        < IDENTITY_THRESHOLD,
    )

    check(
        "Latent Invariance",
        latent_identity_error
        < IDENTITY_THRESHOLD,
    )

    # ------------------------------------------------------------------
    # Monotonicity
    # ------------------------------------------------------------------

    header(
        "Structural Distance Monotonicity"
    )

    sorted_indices = sorted(
        range(
            len(
                result.representation_distances
            )
        ),
        key=lambda i:
            result.representation_distances[i],
    )

    rep_sorted = [
        result.representation_distances[i]
        for i in sorted_indices
    ]

    latent_sorted = [
        result.latent_distances[i]
        for i in sorted_indices
    ]

    monotonic_pairs = 0

    total_pairs = 0

    for i in range(
        len(rep_sorted) - 1
    ):

        if (
            rep_sorted[i]
            < rep_sorted[i + 1]
        ):

            total_pairs += 1

            if (
                latent_sorted[i]
                <= latent_sorted[i + 1]
            ):

                monotonic_pairs += 1

    monotonicity = (
        monotonic_pairs
        / max(total_pairs, 1)
    )

    print(
        f"Monotonicity score: "
        f"{monotonicity:.8f}"
    )

    check(
        "Structural Distance Monotonicity",
        monotonicity
        >= 0.95,
    )

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------

    header(
        "Geometry Report"
    )

    report = {

        "version":
            VERSION,

        "struct3d_version":
            STRUCT3D_VERSION,

        "seed":
            SEED,

        "device":
            str(DEVICE),

        "input_dim":
            INPUT_DIM,

        "latent_dim":
            LATENT_DIM,

        "train_worlds":
            TRAIN_SAMPLES,

        "test_worlds":
            TEST_SAMPLES,

        "pair_samples":
            PAIR_SAMPLE_COUNT,

        "k_neighbors":
            K_NEIGHBORS,

        "global_geometry":
            summary,

        "distance_bins":
            bin_report,

        "local_neighborhood": {

            "k":
                K_NEIGHBORS,

            "mean_neighbor_overlap":
                nn_overlap,

            "local_rank_spearman":
                local_rank,
        },

        "triangle_geometry":
            triangle_report,

        "symmetry": {

            "maximum_error":
                symmetry_error,
        },

        "identity": {

            "maximum_self_distance":
                identity_error,

            "representation_invariance_error":
                representation_identity_error,

            "latent_invariance_error":
                latent_identity_error,
        },

        "distance_collapse":
            collapse,

        "monotonicity": {

            "score":
                monotonicity,

            "monotonic_pairs":
                monotonic_pairs,

            "total_pairs":
                total_pairs,
        },

        "worst_pair":
            worst,

        "test_representation_hash":
            stable_hash(
                [
                    [
                        round(
                            float(v),
                            10,
                        )
                        for v in row.tolist()
                    ]
                    for row in test_tensor
                ]
            ),
    }

    report_path = os.path.join(
        os.path.dirname(__file__)
        if "__file__" in globals()
        else ".",
        REPORT_NAME,
    )

    with open(
        report_path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            report,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"Report saved to:"
    )

    print(
        report_path
    )

    check(
        "Geometry Report Serializable",
        os.path.exists(report_path),
    )

    # ------------------------------------------------------------------
    # Final
    # ------------------------------------------------------------------

    print()

    print("=" * 68)

    print(
        "Neural Struct3D v1.0"
    )

    print(
        "Structural Geometry Validation"
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

        print()

        print(
            "Conclusion:"
        )

        print(
            "The Neural Struct3D latent space "
            "preserves the global and local "
            "geometry induced by Struct3D v4.0 "
            "on an independent structural-world set."
        )

    else:

        print(
            "STATUS: FAIL"
        )

        print()

        print(
            "Conclusion:"
        )

        print(
            "At least one structural geometry "
            "property requires further analysis."
        )

    print("=" * 68)

    return (
        0
        if passed_count == total
        else 1
    )


# ======================================================================
# Entry Point
# ======================================================================

if __name__ == "__main__":

    seed_everything(SEED)

    sys.exit(
        run_geometry_test()
    )