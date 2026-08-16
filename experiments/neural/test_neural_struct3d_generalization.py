#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
======================================================================
Neural Struct3D v1.0
Generalization & Structural Geometry Validation
======================================================================

Purpose
-------

The Neural Struct3D v1.0 regression suite has already established that
the model can preserve Structural Distance on the synthetic training
distribution.

This experiment asks the more important question:

    Does the learned latent geometry generalize to unseen
    Structural Worlds?

Therefore this script performs a strict train/test separation.

    Structural Worlds
            |
            +--------------------+
            |                    |
            v                    v
       TRAIN WORLDS          TEST WORLDS
            |                    |
            v                    |
       Neural Struct3D           |
         training                |
                                 |
                                 v
                     Unseen Structural Geometry
                              Validation

No test world is used during training.

Main evaluations
----------------

1. Train/test separation
2. Test reconstruction
3. Test pairwise Structural Distance preservation
4. Pearson correlation
5. Spearman correlation
6. Relative-error statistics
7. Structural-distance bins
8. Hardest pair analysis
9. Mutation-family generalization
10. Serialization of final evaluation report

Important
---------

This script intentionally does NOT modify:

    run_neural_struct3d.py

The existing v1.0 regression suite remains the frozen baseline.

This file is an evaluation experiment only.

CPU only.
No CUDA.
No Open3D.
No external dataset.

======================================================================
"""

from __future__ import annotations

import copy
import json
import math
import os
import random
import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any, Callable

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

TRAIN_WORLDS = 800
TEST_WORLDS = 200

TRAIN_EPOCHS = 240
LEARNING_RATE = 1e-3

DISTANCE_LOSS_WEIGHT = 1.0

PAIR_COUNT = 10000

RECONSTRUCTION_THRESHOLD = 0.08

MEAN_RELATIVE_ERROR_THRESHOLD = 0.20
PEARSON_THRESHOLD = 0.90
SPEARMAN_THRESHOLD = 0.90

EPSILON = 1e-8

DEVICE = torch.device("cpu")


# ======================================================================
# Deterministic Environment
# ======================================================================

def seed_everything(seed: int = SEED) -> None:
    random.seed(seed)

    torch.manual_seed(seed)

    if hasattr(torch, "use_deterministic_algorithms"):
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
# Structural World
# ======================================================================

from dataclasses import dataclass


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

    total = max(
        len(world.units),
        1,
    )

    return [
        counts.get(p, 0) / total
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


def relation_type_histogram(
    world: World,
) -> List[float]:

    counts = {
        r: 0
        for r in RELATION_TYPES
    }

    for relation in world.relations.values():

        if relation.relation_type not in counts:
            counts[relation.relation_type] = 0

        counts[relation.relation_type] += 1

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

    for instance in world.instances.values():

        if instance.object_id not in counts:
            counts[instance.object_id] = 0

        counts[instance.object_id] += 1

    values = list(
        counts.values()
    )

    return (
        sum(v == 0 for v in values) / len(values),
        sum(v == 1 for v in values) / len(values),
        sum(v >= 2 for v in values) / len(values),
    )


def structural_representation(
    world: World,
) -> List[float]:

    features: List[float] = []

    # --------------------------------------------------------------
    # 0:3 primitive histogram
    # --------------------------------------------------------------

    features.extend(
        primitive_histogram(world)
    )

    # --------------------------------------------------------------
    # 3:6 object composition
    # --------------------------------------------------------------

    features.extend(
        object_histogram(world)
    )

    # --------------------------------------------------------------
    # 6:9 object topology
    # --------------------------------------------------------------

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

    # --------------------------------------------------------------
    # 9:12 relation type
    # --------------------------------------------------------------

    features.extend(
        relation_type_histogram(world)
    )

    # --------------------------------------------------------------
    # 12:15 relation confidence
    # --------------------------------------------------------------

    mean, std, minimum = \
        relation_confidence_statistics(world)

    features.extend([
        mean,
        std,
        minimum,
    ])

    # --------------------------------------------------------------
    # 15:18 instance occupancy
    # --------------------------------------------------------------

    features.extend(
        instance_occupancy(world)
    )

    # --------------------------------------------------------------
    # 18:23 global counts
    # --------------------------------------------------------------

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
            f"Expected {INPUT_DIM} features, "
            f"got {len(features)}"
        )

    return [
        float(x)
        for x in features
    ]


# ======================================================================
# Structural Distance
# ======================================================================

def representation_tensor(
    world: World,
) -> torch.Tensor:

    return torch.tensor(
        structural_representation(world),
        dtype=torch.float32,
        device=DEVICE,
    )


def structural_distance(
    world_a: World,
    world_b: World,
) -> float:

    a = representation_tensor(world_a)
    b = representation_tensor(world_b)

    return float(
        torch.linalg.vector_norm(
            a - b
        ).item()
    )


# ======================================================================
# Random Structural World Generator
# ======================================================================

def random_structural_world(
    rng: random.Random,
) -> World:

    world = make_base_world()

    # --------------------------------------------------------------
    # Primitive state
    # --------------------------------------------------------------

    for uid in world.units:

        if rng.random() < 0.65:

            world.units[uid].primitive = \
                rng.choice(PRIMITIVES)

    # --------------------------------------------------------------
    # Continuous unit attributes
    #
    # These are intentionally NOT represented by the current v4.0
    # representation. They are kept here only to make sure the world
    # generator itself remains structurally diverse without changing
    # the current representation semantics.
    # --------------------------------------------------------------

    for uid in world.units:

        world.units[uid].scale = round(
            rng.uniform(
                0.5,
                2.0,
            ),
            3,
        )

        world.units[uid].fit = round(
            rng.uniform(
                0.01,
                0.5,
            ),
            3,
        )

    # --------------------------------------------------------------
    # Object composition
    # --------------------------------------------------------------

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

        world.objects[oid].units = tuple(
            sorted(selected)
        )

    # --------------------------------------------------------------
    # Instance ownership
    # --------------------------------------------------------------

    object_ids = list(
        world.objects.keys()
    )

    for iid in world.instances:

        world.instances[iid].object_id = \
            rng.choice(object_ids)

    # --------------------------------------------------------------
    # Relation states
    # --------------------------------------------------------------

    for rid in world.relations:

        world.relations[rid].relation_type = \
            rng.choice(RELATION_TYPES)

        world.relations[rid].confidence = round(
            rng.uniform(
                0.1,
                1.0,
            ),
            3,
        )

    # --------------------------------------------------------------
    # Optional relation deletion
    # --------------------------------------------------------------

    if rng.random() < 0.15:

        delete_id = rng.choice(
            list(world.relations.keys())
        )

        del world.relations[
            delete_id
        ]

    return world


# ======================================================================
# Dataset Construction
# ======================================================================

@dataclass
class StructuralDataset:

    worlds: List[World]
    vectors: torch.Tensor


def build_world_dataset(
    n: int,
    seed: int,
) -> StructuralDataset:

    rng = random.Random(seed)

    worlds: List[World] = []
    vectors: List[List[float]] = []

    for _ in range(n):

        world = random_structural_world(
            rng
        )

        worlds.append(world)

        vectors.append(
            structural_representation(
                world
            )
        )

    x = torch.tensor(
        vectors,
        dtype=torch.float32,
        device=DEVICE,
    )

    return StructuralDataset(
        worlds=worlds,
        vectors=x,
    )


# ======================================================================
# Neural Model
# ======================================================================

class StructuralEncoder(nn.Module):

    def __init__(
        self,
        input_dim: int = INPUT_DIM,
        hidden_dim_1: int = HIDDEN_DIM_1,
        hidden_dim_2: int = HIDDEN_DIM_2,
        latent_dim: int = LATENT_DIM,
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
        x: torch.Tensor,
    ) -> torch.Tensor:

        return self.net(x)


class StructuralDecoder(nn.Module):

    def __init__(
        self,
        latent_dim: int = LATENT_DIM,
        hidden_dim_1: int = HIDDEN_DIM_1,
        hidden_dim_2: int = HIDDEN_DIM_2,
        output_dim: int = INPUT_DIM,
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
        z: torch.Tensor,
    ) -> torch.Tensor:

        return self.net(z)


class NeuralStruct3D(nn.Module):

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
    ) -> Tuple[torch.Tensor, torch.Tensor]:

        z = self.encode(x)

        x_hat = self.decode(z)

        return z, x_hat


# ======================================================================
# Pairwise Distance Loss
# ======================================================================

def pairwise_distance_loss(
    z: torch.Tensor,
    x: torch.Tensor,
) -> torch.Tensor:

    latent_distances = torch.cdist(
        z,
        z,
        p=2,
    )

    structural_distances = torch.cdist(
        x,
        x,
        p=2,
    )

    mask = torch.triu(
        torch.ones_like(
            structural_distances,
            dtype=torch.bool,
        ),
        diagonal=1,
    )

    latent_values = \
        latent_distances[mask]

    structural_values = \
        structural_distances[mask]

    return F.mse_loss(
        latent_values,
        structural_values,
    )


# ======================================================================
# Training
# ======================================================================

@dataclass
class TrainingResult:

    initial_total: float
    final_total: float

    initial_reconstruction: float
    final_reconstruction: float

    initial_distance: float
    final_distance: float


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

    initial_total = None
    final_total = None

    initial_reconstruction = None
    final_reconstruction = None

    initial_distance = None
    final_distance = None

    model.train()

    for epoch in range(
        1,
        epochs + 1,
    ):

        optimizer.zero_grad()

        z, x_hat = model(x)

        reconstruction_loss = \
            F.mse_loss(
                x_hat,
                x,
            )

        distance_loss = \
            pairwise_distance_loss(
                z,
                x,
            )

        total_loss = (
            reconstruction_loss
            + DISTANCE_LOSS_WEIGHT
            * distance_loss
        )

        total_loss.backward()

        optimizer.step()

        total_value = float(
            total_loss.detach().cpu().item()
        )

        recon_value = float(
            reconstruction_loss.detach()
            .cpu()
            .item()
        )

        distance_value = float(
            distance_loss.detach()
            .cpu()
            .item()
        )

        if initial_total is None:

            initial_total = total_value
            initial_reconstruction = \
                recon_value
            initial_distance = \
                distance_value

        final_total = total_value
        final_reconstruction = \
            recon_value
        final_distance = \
            distance_value

        if (
            epoch == 1
            or epoch % 40 == 0
            or epoch == epochs
        ):

            print(
                f"Epoch {epoch:03d}/{epochs}: "
                f"total={total_value:.8f} "
                f"recon={recon_value:.8f} "
                f"distance={distance_value:.8f}"
            )

    return TrainingResult(
        initial_total=float(
            initial_total
        ),
        final_total=float(
            final_total
        ),
        initial_reconstruction=float(
            initial_reconstruction
        ),
        final_reconstruction=float(
            final_reconstruction
        ),
        initial_distance=float(
            initial_distance
        ),
        final_distance=float(
            final_distance
        ),
    )


# ======================================================================
# Encoding
# ======================================================================

def encode_dataset(
    model: NeuralStruct3D,
    x: torch.Tensor,
) -> torch.Tensor:

    model.eval()

    with torch.no_grad():

        z = model.encode(x)

    return z


# ======================================================================
# Reconstruction Metrics
# ======================================================================

def reconstruction_metrics(
    model: NeuralStruct3D,
    x: torch.Tensor,
) -> Dict[str, float]:

    model.eval()

    with torch.no_grad():

        z = model.encode(x)

        x_hat = model.decode(z)

    absolute_error = torch.abs(
        x_hat - x
    )

    return {
        "mae": float(
            torch.mean(
                absolute_error
            ).item()
        ),
        "max_absolute_error": float(
            torch.max(
                absolute_error
            ).item()
        ),
    }


# ======================================================================
# Rank Computation
# ======================================================================

def rankdata(
    values: List[float],
) -> List[float]:

    n = len(values)

    indexed = sorted(
        enumerate(values),
        key=lambda item: item[1],
    )

    ranks = [0.0] * n

    i = 0

    while i < n:

        j = i

        while (
            j + 1 < n
            and indexed[j + 1][1]
            == indexed[i][1]
        ):
            j += 1

        average_rank = (
            i + j
        ) / 2.0 + 1.0

        for k in range(
            i,
            j + 1,
        ):

            original_index = \
                indexed[k][0]

            ranks[original_index] = \
                average_rank

        i = j + 1

    return ranks


# ======================================================================
# Correlation
# ======================================================================

def pearson_correlation(
    a: List[float],
    b: List[float],
) -> float:

    if len(a) != len(b):
        raise ValueError(
            "Input lengths differ."
        )

    if len(a) < 2:
        return 0.0

    ta = torch.tensor(
        a,
        dtype=torch.float64,
    )

    tb = torch.tensor(
        b,
        dtype=torch.float64,
    )

    ta = ta - ta.mean()
    tb = tb - tb.mean()

    denominator = (
        torch.linalg.vector_norm(ta)
        * torch.linalg.vector_norm(tb)
    )

    if float(denominator.item()) < EPSILON:
        return 0.0

    return float(
        (
            torch.dot(
                ta,
                tb,
            )
            / denominator
        ).item()
    )


def spearman_correlation(
    a: List[float],
    b: List[float],
) -> float:

    return pearson_correlation(
        rankdata(a),
        rankdata(b),
    )


# ======================================================================
# Pair Sampling
# ======================================================================

@dataclass
class PairMetrics:

    structural_distances: List[float]
    latent_distances: List[float]
    relative_errors: List[float]

    pair_indices: List[Tuple[int, int]]


def sample_test_pairs(
    n: int,
    pair_count: int,
    seed: int,
) -> List[Tuple[int, int]]:

    rng = random.Random(seed)

    maximum_pairs = (
        n * (n - 1)
    ) // 2

    target = min(
        pair_count,
        maximum_pairs,
    )

    selected = set()

    while len(selected) < target:

        i = rng.randrange(n)
        j = rng.randrange(n)

        if i == j:
            continue

        if i > j:
            i, j = j, i

        selected.add(
            (i, j)
        )

    return list(selected)


def evaluate_pairs(
    x: torch.Tensor,
    z: torch.Tensor,
    pairs: List[Tuple[int, int]],
) -> PairMetrics:

    structural_distances = []
    latent_distances = []
    relative_errors = []

    for i, j in pairs:

        structural = float(
            torch.linalg.vector_norm(
                x[i] - x[j]
            ).item()
        )

        latent = float(
            torch.linalg.vector_norm(
                z[i] - z[j]
            ).item()
        )

        if structural > EPSILON:

            relative = abs(
                latent - structural
            ) / structural

        else:

            relative = 0.0

        structural_distances.append(
            structural
        )

        latent_distances.append(
            latent
        )

        relative_errors.append(
            relative
        )

    return PairMetrics(
        structural_distances=
            structural_distances,
        latent_distances=
            latent_distances,
        relative_errors=
            relative_errors,
        pair_indices=pairs,
    )


# ======================================================================
# Percentiles
# ======================================================================

def percentile(
    values: List[float],
    q: float,
) -> float:

    if not values:
        return 0.0

    ordered = sorted(values)

    if len(ordered) == 1:
        return ordered[0]

    position = (
        q / 100.0
    ) * (
        len(ordered) - 1
    )

    lower = int(
        math.floor(position)
    )

    upper = int(
        math.ceil(position)
    )

    if lower == upper:
        return ordered[lower]

    fraction = position - lower

    return (
        ordered[lower]
        * (1.0 - fraction)
        + ordered[upper]
        * fraction
    )


# ======================================================================
# Distance Statistics
# ======================================================================

def distance_statistics(
    metrics: PairMetrics,
) -> Dict[str, float]:

    errors = metrics.relative_errors

    return {
        "mean_relative_error":
            sum(errors)
            / max(len(errors), 1),

        "median_relative_error":
            percentile(
                errors,
                50.0,
            ),

        "p90_relative_error":
            percentile(
                errors,
                90.0,
            ),

        "p95_relative_error":
            percentile(
                errors,
                95.0,
            ),

        "max_relative_error":
            max(errors)
            if errors
            else 0.0,

        "pearson":
            pearson_correlation(
                metrics.structural_distances,
                metrics.latent_distances,
            ),

        "spearman":
            spearman_correlation(
                metrics.structural_distances,
                metrics.latent_distances,
            ),

        "pair_count":
            len(errors),
    }


# ======================================================================
# Distance Bin Analysis
# ======================================================================

DISTANCE_BINS = [
    (0.0, 0.2),
    (0.2, 0.4),
    (0.4, 0.6),
    (0.6, 0.8),
    (0.8, 1.0),
    (1.0, 1.5),
    (1.5, float("inf")),
]


def distance_bin_analysis(
    metrics: PairMetrics,
) -> List[Dict[str, Any]]:

    results = []

    for lower, upper in DISTANCE_BINS:

        selected = []

        for structural, error in zip(
            metrics.structural_distances,
            metrics.relative_errors,
        ):

            if (
                structural >= lower
                and structural < upper
            ):
                selected.append(error)

        if selected:

            mean_error = (
                sum(selected)
                / len(selected)
            )

            median_error = percentile(
                selected,
                50.0,
            )

            p90_error = percentile(
                selected,
                90.0,
            )

        else:

            mean_error = 0.0
            median_error = 0.0
            p90_error = 0.0

        results.append({
            "lower": lower,
            "upper": upper,
            "count": len(selected),
            "mean_relative_error":
                mean_error,
            "median_relative_error":
                median_error,
            "p90_relative_error":
                p90_error,
        })

    return results


# ======================================================================
# Hardest Pair
# ======================================================================

def hardest_pair(
    metrics: PairMetrics,
    worlds: List[World],
    x: torch.Tensor,
    z: torch.Tensor,
) -> Dict[str, Any]:

    if not metrics.relative_errors:
        return {}

    index = max(
        range(
            len(
                metrics.relative_errors
            )
        ),
        key=lambda i:
            metrics.relative_errors[i],
    )

    i, j = metrics.pair_indices[index]

    structural = \
        metrics.structural_distances[index]

    latent = \
        metrics.latent_distances[index]

    relative = \
        metrics.relative_errors[index]

    representation_i = [
        float(v)
        for v in x[i].cpu().tolist()
    ]

    representation_j = [
        float(v)
        for v in x[j].cpu().tolist()
    ]

    difference = [
        abs(a - b)
        for a, b in zip(
            representation_i,
            representation_j,
        )
    ]

    dominant_dimensions = sorted(
        range(INPUT_DIM),
        key=lambda k:
            difference[k],
        reverse=True,
    )[:5]

    return {
        "pair_index": index,
        "world_i": i,
        "world_j": j,
        "structural_distance":
            structural,
        "latent_distance":
            latent,
        "relative_error":
            relative,
        "representation_i":
            representation_i,
        "representation_j":
            representation_j,
        "absolute_representation_difference":
            difference,
        "top_difference_dimensions":
            dominant_dimensions,
    }


# ======================================================================
# Mutation Families
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

    if "R0" in result.relations:

        result.relations[
            "R0"
        ].relation_type = "contains"

    return result


def mutate_relation_confidence(
    world: World,
) -> World:

    result = clone_world(world)

    if "R0" in result.relations:

        result.relations[
            "R0"
        ].confidence = 0.25

    return result


def mutate_relation_deletion(
    world: World,
) -> World:

    result = clone_world(world)

    if "R1" in result.relations:

        del result.relations["R1"]

    elif result.relations:

        first = next(
            iter(result.relations)
        )

        del result.relations[first]

    return result


MUTATIONS: Dict[
    str,
    Callable[[World], World]
] = {
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


# ======================================================================
# Mutation Generalization
# ======================================================================

def evaluate_mutation_family(
    model: NeuralStruct3D,
    worlds: List[World],
) -> Dict[str, Any]:

    model.eval()

    family_results = {}

    for name, mutation in MUTATIONS.items():

        representation_errors = []
        latent_errors = []

        valid_count = 0

        for world in worlds:

            mutated = mutation(world)

            x_a = representation_tensor(
                world
            ).unsqueeze(0)

            x_b = representation_tensor(
                mutated
            ).unsqueeze(0)

            with torch.no_grad():

                z_a = model.encode(x_a)
                z_b = model.encode(x_b)

            d_rep = float(
                torch.linalg.vector_norm(
                    x_a - x_b
                ).item()
            )

            d_latent = float(
                torch.linalg.vector_norm(
                    z_a - z_b
                ).item()
            )

            if d_rep > EPSILON:

                relative_error = abs(
                    d_latent - d_rep
                ) / d_rep

                representation_errors.append(
                    d_rep
                )

                latent_errors.append(
                    d_latent
                )

                valid_count += 1

        if valid_count > 0:

            relative_errors = [
                abs(
                    z - r
                ) / r
                for r, z in zip(
                    representation_errors,
                    latent_errors,
                )
            ]

            family_results[name] = {
                "count": valid_count,
                "mean_representation_distance":
                    sum(
                        representation_errors
                    ) / valid_count,
                "mean_latent_distance":
                    sum(
                        latent_errors
                    ) / valid_count,
                "mean_relative_error":
                    sum(
                        relative_errors
                    ) / valid_count,
                "median_relative_error":
                    percentile(
                        relative_errors,
                        50.0,
                    ),
                "max_relative_error":
                    max(
                        relative_errors
                    ),
            }

        else:

            family_results[name] = {
                "count": 0,
                "mean_representation_distance": 0.0,
                "mean_latent_distance": 0.0,
                "mean_relative_error": 0.0,
                "median_relative_error": 0.0,
                "max_relative_error": 0.0,
            }

    return family_results


# ======================================================================
# Report Serialization
# ======================================================================

def save_report(
    report: Dict[str, Any],
    path: str,
) -> None:

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            report,
            f,
            indent=2,
            ensure_ascii=False,
        )


# ======================================================================
# Main Experiment
# ======================================================================

def main() -> int:

    print("=" * 68)
    print(
        "Neural Struct3D v1.0"
    )
    print(
        "Generalization & Structural Geometry Validation"
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
        f"Train worlds: {TRAIN_WORLDS}"
    )

    print(
        f"Test worlds: {TEST_WORLDS}"
    )

    print(
        f"Test pairs: {PAIR_COUNT}"
    )

    print(
        f"Distance loss weight: "
        f"{DISTANCE_LOSS_WEIGHT}"
    )

    # ==============================================================
    # Generate train/test
    # ==============================================================

    header(
        "Strict Train/Test Structural World Split"
    )

    train_dataset = build_world_dataset(
        TRAIN_WORLDS,
        SEED + 100,
    )

    test_dataset = build_world_dataset(
        TEST_WORLDS,
        SEED + 200,
    )

    print(
        f"Train tensor shape: "
        f"{tuple(train_dataset.vectors.shape)}"
    )

    print(
        f"Test tensor shape: "
        f"{tuple(test_dataset.vectors.shape)}"
    )

    check_train_unique = (
        torch.unique(
            train_dataset.vectors,
            dim=0,
        ).shape[0]
        == TRAIN_WORLDS
    )

    check_test_unique = (
        torch.unique(
            test_dataset.vectors,
            dim=0,
        ).shape[0]
        == TEST_WORLDS
    )

    if check_train_unique:
        passed(
            "Train Worlds Have Unique Structural Representations"
        )
    else:
        failed(
            "Train Worlds Have Unique Structural Representations"
        )

    if check_test_unique:
        passed(
            "Test Worlds Have Unique Structural Representations"
        )
    else:
        failed(
            "Test Worlds Have Unique Structural Representations"
        )

    # ==============================================================
    # Explicit train/test representation overlap
    # ==============================================================

    train_hashes = {
        tuple(
            round(
                float(v),
                8,
            )
            for v in row.tolist()
        )
        for row in train_dataset.vectors
    }

    test_hashes = {
        tuple(
            round(
                float(v),
                8,
            )
            for v in row.tolist()
        )
        for row in test_dataset.vectors
    }

    overlap = train_hashes.intersection(
        test_hashes
    )

    print(
        f"Train/test representation overlap: "
        f"{len(overlap)}"
    )

    if len(overlap) == 0:
        passed(
            "Train/Test Structural Representations Are Disjoint"
        )
    else:
        failed(
            "Train/Test Structural Representations Are Disjoint"
        )

    # ==============================================================
    # Model
    # ==============================================================

    header(
        "Neural Struct3D Training"
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

    training = train_model(
        model,
        train_dataset.vectors,
    )

    print()
    print(
        f"Initial total loss: "
        f"{training.initial_total:.10f}"
    )

    print(
        f"Final total loss:   "
        f"{training.final_total:.10f}"
    )

    print(
        f"Initial reconstruction: "
        f"{training.initial_reconstruction:.10f}"
    )

    print(
        f"Final reconstruction:   "
        f"{training.final_reconstruction:.10f}"
    )

    print(
        f"Initial distance loss: "
        f"{training.initial_distance:.10f}"
    )

    print(
        f"Final distance loss:   "
        f"{training.final_distance:.10f}"
    )

    if (
        training.final_total
        < training.initial_total
    ):
        passed(
            "Training Total Loss Decreases"
        )
    else:
        failed(
            "Training Total Loss Decreases"
        )

    if (
        training.final_distance
        < training.initial_distance
    ):
        passed(
            "Training Distance Loss Decreases"
        )
    else:
        failed(
            "Training Distance Loss Decreases"
        )

    # ==============================================================
    # Test Reconstruction
    # ==============================================================

    header(
        "Unseen Test World Reconstruction"
    )

    test_reconstruction = \
        reconstruction_metrics(
            model,
            test_dataset.vectors,
        )

    print(
        f"Test reconstruction MAE: "
        f"{test_reconstruction['mae']:.10f}"
    )

    print(
        f"Test maximum absolute error: "
        f"{test_reconstruction['max_absolute_error']:.10f}"
    )

    if (
        test_reconstruction["mae"]
        < RECONSTRUCTION_THRESHOLD
    ):
        passed(
            "Unseen Test Reconstruction"
        )
    else:
        failed(
            "Unseen Test Reconstruction"
        )

    # ==============================================================
    # Test latent encoding
    # ==============================================================

    header(
        "Unseen Test Latent Encoding"
    )

    test_latent = encode_dataset(
        model,
        test_dataset.vectors,
    )

    print(
        f"Test latent shape: "
        f"{tuple(test_latent.shape)}"
    )

    if tuple(
        test_latent.shape
    ) == (
        TEST_WORLDS,
        LATENT_DIM,
    ):
        passed(
            "Test Latent Dimension"
        )
    else:
        failed(
            "Test Latent Dimension"
        )

    # ==============================================================
    # Pairwise Structural Geometry
    # ==============================================================

    header(
        "Unseen Test Pairwise Structural Geometry"
    )

    pairs = sample_test_pairs(
        TEST_WORLDS,
        PAIR_COUNT,
        SEED + 300,
    )

    print(
        f"Evaluated pairs: "
        f"{len(pairs)}"
    )

    metrics = evaluate_pairs(
        test_dataset.vectors,
        test_latent,
        pairs,
    )

    statistics = distance_statistics(
        metrics
    )

    print(
        f"mean_relative_error     : "
        f"{statistics['mean_relative_error']:.8f}"
    )

    print(
        f"median_relative_error   : "
        f"{statistics['median_relative_error']:.8f}"
    )

    print(
        f"p90_relative_error      : "
        f"{statistics['p90_relative_error']:.8f}"
    )

    print(
        f"p95_relative_error      : "
        f"{statistics['p95_relative_error']:.8f}"
    )

    print(
        f"max_relative_error      : "
        f"{statistics['max_relative_error']:.8f}"
    )

    print(
        f"pearson                 : "
        f"{statistics['pearson']:.8f}"
    )

    print(
        f"spearman                : "
        f"{statistics['spearman']:.8f}"
    )

    print(
        f"pair_count              : "
        f"{statistics['pair_count']}"
    )

    if (
        statistics[
            "mean_relative_error"
        ]
        < MEAN_RELATIVE_ERROR_THRESHOLD
    ):
        passed(
            "Unseen Pair Distance Relative Error"
        )
    else:
        failed(
            "Unseen Pair Distance Relative Error"
        )

    if (
        statistics["pearson"]
        >= PEARSON_THRESHOLD
    ):
        passed(
            "Unseen Pair Pearson Correlation"
        )
    else:
        failed(
            "Unseen Pair Pearson Correlation"
        )

    if (
        statistics["spearman"]
        >= SPEARMAN_THRESHOLD
    ):
        passed(
            "Unseen Pair Spearman Correlation"
        )
    else:
        failed(
            "Unseen Pair Spearman Correlation"
        )

    # ==============================================================
    # Distance bins
    # ==============================================================

    header(
        "Structural Distance Bin Analysis"
    )

    bins = distance_bin_analysis(
        metrics
    )

    for item in bins:

        lower = item["lower"]
        upper = item["upper"]

        if math.isinf(upper):
            label = f"{lower:.1f}+"
        else:
            label = (
                f"{lower:.1f}-"
                f"{upper:.1f}"
            )

        print(
            f"{label:10s} "
            f"count={item['count']:5d} "
            f"mean={item['mean_relative_error']:.6f} "
            f"median={item['median_relative_error']:.6f} "
            f"p90={item['p90_relative_error']:.6f}"
        )

    # ==============================================================
    # Hardest pair
    # ==============================================================

    header(
        "Hardest Unseen Structural Pair"
    )

    hardest = hardest_pair(
        metrics,
        test_dataset.worlds,
        test_dataset.vectors,
        test_latent,
    )

    if hardest:

        print(
            f"World i: "
            f"{hardest['world_i']}"
        )

        print(
            f"World j: "
            f"{hardest['world_j']}"
        )

        print(
            f"Structural distance: "
            f"{hardest['structural_distance']:.12f}"
        )

        print(
            f"Latent distance: "
            f"{hardest['latent_distance']:.12f}"
        )

        print(
            f"Relative error: "
            f"{hardest['relative_error']:.8f}"
        )

        print(
            "Top representation difference "
            "dimensions:"
        )

        for dimension in \
            hardest[
                "top_difference_dimensions"
            ]:

            print(
                f"  dim {dimension:02d}: "
                f"{hardest['absolute_representation_difference'][dimension]:.8f}"
            )

    # ==============================================================
    # Mutation-family validation
    # ==============================================================

    header(
        "Mutation-Family Generalization"
    )

    mutation_results = \
        evaluate_mutation_family(
            model,
            test_dataset.worlds,
        )

    for name, result in \
        mutation_results.items():

        print(
            f"{name:20s} "
            f"count={result['count']:4d} "
            f"R={result['mean_representation_distance']:.6f} "
            f"Z={result['mean_latent_distance']:.6f} "
            f"mean_error={result['mean_relative_error']:.6f} "
            f"median={result['median_relative_error']:.6f} "
            f"max={result['max_relative_error']:.6f}"
        )

    valid_mutation_results = [
        result
        for result in mutation_results.values()
        if result["count"] > 0
    ]

    mutation_mean_error = (
        sum(
            r["mean_relative_error"]
            for r in valid_mutation_results
        )
        / max(
            len(valid_mutation_results),
            1,
        )
    )

    if (
        mutation_mean_error
        < MEAN_RELATIVE_ERROR_THRESHOLD
    ):
        passed(
            "Mutation-Family Structural Geometry Generalization"
        )
    else:
        failed(
            "Mutation-Family Structural Geometry Generalization"
        )

    # ==============================================================
    # Final report
    # ==============================================================

    report = {
        "version": VERSION,
        "struct3d_version":
            STRUCT3D_VERSION,

        "seed": SEED,

        "device":
            str(DEVICE),

        "input_dim":
            INPUT_DIM,

        "latent_dim":
            LATENT_DIM,

        "train_worlds":
            TRAIN_WORLDS,

        "test_worlds":
            TEST_WORLDS,

        "pair_count":
            len(pairs),

        "train_test_representation_overlap":
            len(overlap),

        "training": {
            "initial_total":
                training.initial_total,
            "final_total":
                training.final_total,
            "initial_reconstruction":
                training.initial_reconstruction,
            "final_reconstruction":
                training.final_reconstruction,
            "initial_distance":
                training.initial_distance,
            "final_distance":
                training.final_distance,
        },

        "test_reconstruction":
            test_reconstruction,

        "pairwise_geometry":
            statistics,

        "distance_bins":
            bins,

        "hardest_pair":
            hardest,

        "mutation_generalization":
            mutation_results,
    }

    report_path = os.path.join(
        os.path.dirname(__file__)
        if "__file__" in globals()
        else ".",
        "neural_struct3d_v1_generalization_report.json",
    )

    save_report(
        report,
        report_path,
    )

    header(
        "Generalization Report"
    )

    print(
        f"Report saved to:\n"
        f"{report_path}"
    )

    # ==============================================================
    # Final status
    # ==============================================================

    critical_passes = [

        (
            len(overlap)
            == 0
        ),

        (
            training.final_total
            < training.initial_total
        ),

        (
            training.final_distance
            < training.initial_distance
        ),

        (
            test_reconstruction[
                "mae"
            ]
            < RECONSTRUCTION_THRESHOLD
        ),

        (
            statistics[
                "mean_relative_error"
            ]
            < MEAN_RELATIVE_ERROR_THRESHOLD
        ),

        (
            statistics[
                "pearson"
            ]
            >= PEARSON_THRESHOLD
        ),

        (
            statistics[
                "spearman"
            ]
            >= SPEARMAN_THRESHOLD
        ),

        (
            mutation_mean_error
            < MEAN_RELATIVE_ERROR_THRESHOLD
        ),
    ]

    print()
    print("=" * 68)
    print(
        "Neural Struct3D v1.0"
    )
    print(
        "Generalization & Structural Geometry Validation"
    )
    print("=" * 68)

    print(
        f"Critical checks: "
        f"{sum(critical_passes)} / "
        f"{len(critical_passes)}"
    )

    if all(critical_passes):

        print(
            "STATUS: PASS"
        )

        print()
        print(
            "Conclusion:"
        )

        print(
            "The Neural Struct3D latent space "
            "preserves the Struct3D v4.0 "
            "Structural Geometry on unseen "
            "synthetic Structural Worlds."
        )

        return 0

    print(
        "STATUS: FAIL"
    )

    print()
    print(
        "Conclusion:"
    )

    print(
        "The current Neural Struct3D model "
        "does not yet satisfy all "
        "generalization criteria."
    )

    return 1


# ======================================================================
# Entry Point
# ======================================================================

if __name__ == "__main__":

    seed_everything(SEED)

    sys.exit(
        main()
    )