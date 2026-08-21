"""Unit-family -> World quotient closure.

Frozen closure theorem
----------------------
For a finite simple observation X, let

    P* in argmin_{P in Gamma(X)} E_2D(P)

and materialize every block A in P* as

    U_X(A) = (A, T_X(A)).

A world is then W_X(P*,R,Phi)=(U,R,Phi), where R and Phi are explicit
quotient-compatible maps. The scalar Stage-2D energy is *not* itself an
injective Unit identifier; the Energy-Induced Unit Equivalence is therefore
defined by the complete admissible energy profile, not by one scalar value.

This distinction is mathematical, not an implementation escape hatch:
scalar equality E_U(u)=E_U(v) is generally insufficient to imply u=v.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence, Tuple

from .theory_candidates import PartitionBlocks, relabel_blocks
from .theory_core import Partition, StructuralUnit
from .theory_observation_theta import observation_unit, theta_signature
from .theory_relation import StructuralRelation
from .theory_world import StructuralWorld
from .theory_energy_model import Observation3D, Stage2DEnergy

EnergyProfile = Tuple[float, ...]


@dataclass(frozen=True)
class QuotientWorld:
    """A frozen world realization together with its observation permutation."""

    world: StructuralWorld
    blocks: PartitionBlocks


def materialize_unit_family(
    observation: Observation3D,
    partition: Partition,
) -> Tuple[StructuralUnit, ...]:
    """Materialize the partition using exactly U_X(A)=(A,T_X(A))."""
    return tuple(observation_unit(observation, unit.indices) for unit in partition.units)


def _unit_index_by_support(units: Sequence[StructuralUnit]):
    return {unit.indices: i for i, unit in enumerate(units)}


def transport_relations(
    relations: Sequence[StructuralRelation],
    unit_map: Mapping[int, int],
) -> Tuple[StructuralRelation, ...]:
    """Transport explicit relations through a unit relabeling."""
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
    """Construct W=(U,R,Phi) from P* without inferring hidden relations."""
    units = materialize_unit_family(observation, partition)
    world = StructuralWorld(
        units=units,
        relations=tuple(relations),
        attributes=dict(phi or {}),
    )
    return QuotientWorld(world=world, blocks=tuple(u.indices for u in units))


def relabel_partition(
    partition: Partition,
    permutation: Mapping[int, int],
) -> PartitionBlocks:
    """Apply the quotient action to a partition's supports."""
    return relabel_blocks(tuple(u.indices for u in partition.units), permutation)


def support_bijection(
    source_units: Sequence[StructuralUnit],
    target_units: Sequence[StructuralUnit],
) -> dict[int, int]:
    """Build the unique unit-index map induced by matching supports."""
    target = _unit_index_by_support(target_units)
    result = {}
    for i, unit in enumerate(source_units):
        j = target.get(unit.indices)
        if j is None:
            raise ValueError("Unit families do not have matching supports")
        result[i] = j
    return result


def unit_quotient_equivalent(u: StructuralUnit, v: StructuralUnit) -> bool:
    """Energy-compatible Unit quotient relation: identical finite theta signature.

    On the frozen simple-observation domain, theta is injective, so this is
    exactly equality of the Unit quotient representative after legal relabeling.
    """
    return theta_signature(u) == theta_signature(v)


def energy_profile(
    unit: StructuralUnit,
    observation: Observation3D,
    energy: Stage2DEnergy,
    contexts: Sequence[Callable[[StructuralUnit], float]] = (),
) -> EnergyProfile:
    """Complete finite admissible energy profile for a Unit.

    The first coordinate is the current Stage-2D scalar unit energy. Additional
    explicit context energies may be supplied. The profile is the object used
    for Energy-Induced Equivalence; a single scalar is deliberately not treated
    as an injective identifier.
    """
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
    """Define energy-induced equivalence by equality of the explicit profile."""
    return energy_profile(u, observation, energy, contexts) == energy_profile(
        v, observation, energy, contexts
    )


def energy_profile_separates_units(
    units: Sequence[StructuralUnit],
    observation: Observation3D,
    energy: Stage2DEnergy,
    contexts: Sequence[Callable[[StructuralUnit], float]] = (),
) -> bool:
    """Finite separation certificate: distinct quotient Units have distinct profiles."""
    profiles = {}
    for unit in units:
        key = tuple(theta_signature(unit))
        profile = energy_profile(unit, observation, energy, contexts)
        previous = profiles.get(profile)
        if previous is not None and previous != key:
            return False
        profiles[profile] = key
    return True


def prove_unit_energy_equivalence_consistency(
    units: Sequence[StructuralUnit],
    observation: Observation3D,
    energy: Stage2DEnergy,
    contexts: Sequence[Callable[[StructuralUnit], float]] = (),
) -> bool:
    """Finite theorem check: energy equivalence equals the frozen Unit quotient.

    This is a proof-by-finite-enumeration contract. It returns True exactly when
    the explicit energy profile separates all distinct frozen theta classes.
    """
    if not energy_profile_separates_units(units, observation, energy, contexts):
        return False
    for i, u in enumerate(units):
        for v in units[i + 1 :]:
            if energy_induced_equivalent(u, v, observation, energy, contexts) != unit_quotient_equivalent(u, v):
                return False
    return True


def world_relabeling(
    world: StructuralWorld,
    unit_permutation: Mapping[int, int],
) -> StructuralWorld:
    """Apply a legal relabeling to W=(U,R,Phi), preserving all semantic payloads."""
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
    """Check P* -> U -> R -> W commutes with a legal observation relabeling."""
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
    # Relation transport is by the induced unit bijection; Phi is copied as an
    # explicitly supplied quotient-invariant payload.
    unit_map = support_bijection(base.units, mapped_units)
    mapped_relations = transport_relations(relations, unit_map)
    mapped_world = StructuralWorld(mapped_units, mapped_relations, dict(phi or {}))
    return tuple(theta_signature(u) for u in base.units) == tuple(theta_signature(u) for u in mapped_world.units) and set(
        (r.source, r.target, r.relation_type) for r in world_relabeling(base, unit_map).relations
    ) == set((r.source, r.target, r.relation_type) for r in mapped_world.relations)


__all__ = [
    "QuotientWorld",
    "materialize_unit_family",
    "transport_relations",
    "build_world",
    "unit_quotient_equivalent",
    "energy_profile",
    "energy_induced_equivalent",
    "energy_profile_separates_units",
    "prove_unit_energy_equivalence_consistency",
    "world_relabeling",
    "world_quotient_compatible",
]
