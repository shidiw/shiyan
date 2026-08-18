"""Theory-facing relation data model for Struct3D.

This module deliberately defines representation, not a new relation law.
The historical relation.py remains available as a legacy implementation.
No relation type, threshold, or fusion rule is promoted to theory here unless
it has an explicit upstream mathematical definition.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Tuple


@dataclass(frozen=True)
class StructuralRelation:
    """A relation record between two structural entities.

    Semantics are supplied by the theory layer.  This class therefore stores
    endpoints, a symbolic type, and optional evidence without deciding how a
    relation is inferred or whether it causes object fusion.
    """

    source: int
    target: int
    relation_type: str
    confidence: Optional[float] = None
    evidence: Mapping[str, Any] = field(default_factory=dict)

    def canonical(self) -> "StructuralRelation":
        """Return a canonical endpoint ordering for an undirected record.

        Canonicalization is purely representational; it does not assert that
        every Struct3D relation is mathematically undirected.
        """
        if self.source <= self.target:
            return self
        return StructuralRelation(
            source=self.target,
            target=self.source,
            relation_type=self.relation_type,
            confidence=self.confidence,
            evidence=dict(self.evidence),
        )

    def key(self) -> Tuple[int, int, str]:
        r = self.canonical()
        return r.source, r.target, r.relation_type


def relation_from_mapping(record: Mapping[str, Any]) -> StructuralRelation:
    """Normalize an existing relation record without changing its semantics."""
    endpoints = record.get("units")
    if endpoints is None:
        endpoints = (record.get("source"), record.get("target"))
    if endpoints is None or len(endpoints) != 2:
        raise ValueError("A relation requires exactly two endpoints")

    relation_type = record.get("type", record.get("relation"))
    if relation_type is None:
        raise ValueError("A relation requires an explicit type")

    confidence = record.get("confidence")
    evidence = dict(record)
    for key in ("units", "source", "target", "type", "relation", "confidence"):
        evidence.pop(key, None)

    return StructuralRelation(
        source=int(endpoints[0]),
        target=int(endpoints[1]),
        relation_type=str(relation_type),
        confidence=None if confidence is None else float(confidence),
        evidence=evidence,
    )
