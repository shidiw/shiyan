"""Unit-family -> World quotient closure.

Frozen closure theorem:

    X -> Gamma(X) -> P* -> U_X(P*) -> R -> W=(U,R,Phi)

commutes with every legal observation relabeling. Energy-induced Unit
Equivalence is defined by a complete explicit admissible energy profile. The
current Stage-2D scalar is one coordinate of that profile and is deliberately
not claimed to be injective by itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence, Tuple

from .theory_candidates import PartitionBlocks, relabel_blocks
from .theory_core import Partition, StructuralUnit
from .theory_energy_model import Observation3D, Stage2DEnergy
from .theory_observation_theta import observation_unit, theta_signature
from .theory_relation import StructuralRelation
from .theory_world import StructuralWorld

EnergyProfile = Tuple[float, ...]


@dataclass(frozen=True)
class QuotientWorld:
    world: StructuralWorld
    blocks: PartitionBlocks


def materialize_unit_family(observation: Observation3D, partition: Partition) -> Tuple[StructuralUnit, ...]:
    """Materialize every partition block as U_X(A)=(A,T_X(A))."""
    return tuple(observation_unit(observation, unit.indices) for unit in partition.units)


def transport_relations(relations: Sequence[StructuralRelation], unit_map: Mapping[int, int]) -> Tuple[StructuralRelation, ...]:
    """Transport the explicit relation set through a unit bijection."""
    return tuple(
        StructuralRelation(
            source=unit_map[r.source],
            target=unit_map[r.target],
            relation_type=r.relation_type,
            evidence=dict(r.evidence),
        )
        for r in relations
    )


def build_world(
    observation: Observation3D,
    partition: Partition,
    relations: Sequence[StructuralRelation],
    phi: Mapping[str, object] | None = None,
) -> QuotientWorld:
    """Construct W=(U,R,Phi) without inferring hidden relations."""
    units = materialize_unit_family(observation, partition)
    return QuotientWorld(
        world=StructuralWorld(units=units, relations=tuple(relations), attributes=dict(phi or {})),
        blocks=tuple(u.indices for u in units),
    )


def relabel_partition(partition: Partition, permutation: Mapping[int, int]) -> PartitionBlocks:
    return relabel_blocks(tuple(u.indices for u in partition.units), permutation)


def unit_bijection_by_theta(
    source_units: Sequence[StructuralUnit],
    target_units: Sequence[StructuralUnit],
) -> dict[int, int]:
    """Match Unit quotient classes by the frozen injective theta representative."""
    target = {}
    for j, unit in enumerate(target_units):
        key = theta_signature(unit)
        if key in target:
            raise ValueError("Target Unit family contains duplicate theta classes")
        target[key] = j
    result = {}
    for i, unit in enumerate(source_units):
        j = target.get(theta_signature(unit))
        if j is None:
            raise ValueError("Unit families do not have matching theta classes")
        result[i] = j
    return result


def unit_quotient_equivalent(u: StructuralUnit, v: StructuralUnit) -> bool:
    """Frozen Unit quotient relation: equality of observation-derived theta."""
    return theta_signature(u) == theta_signature(v)


def energy_profile(
    unit: StructuralUnit,
    observation: Observation3D,
    energy: Stage2DEnergy,
    contexts: Sequence[Callable[[StructuralUnit], float]] = (),
) -> EnergyProfile:
    """Finite admissible energy profile; coordinate 0 is the Stage-2D unit term."""
    if energy.observation != observation:
        raise ValueError("Energy and observation must agree")
    values = [energy.unit_energy(unit)]
    values.extend(float(context(unit)) for context in contexts)
    return tuple(values)


def energy_induced_equivalent(
    u: StructuralUnit,
    v: StructuralUnit,
    observation: Observation3D,
    energy: Stage2DEnergy,
    contexts: Sequence[Callable[[StructuralUnit], float]] = (),
) -> bool:
    """Energy-induced equivalence = equality of the complete explicit profile."""
    return energy_profile(u, observation, energy, contexts) == energy_profile(v, observation, energy, contexts)


def energy_profile_separates_units(
    units: Sequence[StructuralUnit],
    observation: Observation3D,
    energy: Stage2DEnergy,
    contexts: Sequence[Callable[[StructuralUnit], float]] = (),
) -> bool:
    """Finite separation certificate for distinct theta quotient classes."""
    profiles = {}
    for unit in units:
        profile = energy_profile(unit, observation, energy, contexts)
        quotient_key = theta_signature(unit)
        previous = profiles.get(profile)
        if previous is not None and previous != quotient_key:
            return False
        profiles[profile] = quotient_key
    return True


def prove_unit_energy_equivalence_consistency(
    units: Sequence[StructuralUnit],
    observation: Observation3D,
    energy: Stage2DEnergy,
    contexts: Sequence[Callable[[StructuralUnit], float]] = (),
) -> bool:
    """Finite proof contract: E-equivalence equals frozen Unit quotient equivalence."""
    if not energy_profile_separates_units(units, observation, energy, contexts):
        return False
    for i, u in enumerate(units):
        for v in units[i + 1 :]:
            if energy_induced_equivalent(u, v, observation, energy, contexts) != unit_quotient_equivalent(u, v):
                return False
    return True


def world_relabeling(world: StructuralWorld, unit_permutation: Mapping[int, int]) -> StructuralWorld:
    """Apply a legal unit relabeling to W=(U,R,Phi)."""
    n = len(world.units)
    if set(unit_permutation) != set(range(n)) or set(unit_permutation.values()) != set(range(n)):
        raise ValueError("Unit permutation must be a bijection")
    units = tuple(world.units[old] for old in sorted(unit_permutation, key=lambda old: unit_permutation[old]))
    relations = transport_relations(world.relations, unit_permutation)
    return StructuralWorld(units=units, relations=relations, attributes=dict(world.attributes))


def world_quotient_compatible(
    observation: Observation3D,
    partition: Partition,
    relations: Sequence[StructuralRelation],
    phi: Mapping[str, object] | None = None,
    observation_permutation: Mapping[int, int] | None = None,
) -> bool:
    """Verify commutativity of P* -> U -> R -> W under observation relabeling."""
    base = build_world(observation, partition, relations, phi).world
    if observation_permutation is None:
        return True
    n = len(observation.points)
    if set(observation_permutation) != set(range(n)) or set(observation_permutation.values()) != set(range(n)):
        return False

    relabeled_points = [None] * n
    for old, new in observation_permutation.items():
        relabeled_points[new] = observation.points[old]
    relabeled_observation = Observation3D(points=tuple(relabeled_points))

    mapped_blocks = relabel_partition(partition, observation_permutation)
    mapped_units = tuple(observation_unit(relabeled_observation, block) for block in mapped_blocks)
    unit_map = unit_bijection_by_theta(base.units, mapped_units)
    mapped_relations = transport_relations(relations, unit_map)
    mapped_world = StructuralWorld(mapped_units, mapped_relations, dict(phi or {}))

    transported = world_relabeling(base, unit_map)
    return (
        tuple(theta_signature(u) for u in transported.units) == tuple(theta_signature(u) for u in mapped_world.units)
        and {(r.source, r.target, r.relation_type) for r in transported.relations}
        == {(r.source, r.target, r.relation_type) for r in mapped_world.relations}
        and dict(transported.attributes) == dict(mapped_world.attributes)
    )


__all__ = [
    "QuotientWorld",
    "materialize_unit_family",
    "transport_relations",
    "build_world",
    "unit_bijection_by_theta",
    "unit_quotient_equivalent",
    "energy_profile",
    "energy_induced_equivalent",
    "energy_profile_separates_units",
    "prove_unit_energy_equivalence_consistency",
    "world_relabeling",
    "world_quotient_compatible",
]
