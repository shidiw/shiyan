"""Observation-derived semantic strength contracts for Struct3D.

This module separates two ideas that were previously conflated:

* M(X) is the finite observation-derived model universe.
* M_X(A) is the subset of M(X) that is actually optimal for one candidate
  Unit A under the frozen local geometric score.

The relation predicate Q_X is also strengthened.  Merely having a finite
positive confidence makes every pair related and therefore has essentially no
semantic separation power.  The frozen Q_X below instead uses a local,
observation-derived scale: two Units are related exactly when their minimum
cross-support distance is no larger than the median pairwise distance inside
A union B.  No external threshold, label, or neural feature is used.
"""

from __future__ import annotations

from math import isfinite, sqrt
from typing import Sequence, Tuple

from .theory_core import StructuralUnit


def point_distance(a, b) -> float:
    return sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def unit_model_scores(unit: StructuralUnit, context) -> Tuple[Tuple[object, float], ...]:
    """Return the finite regularized model scores for one candidate Unit A."""
    points = context.observation.points
    if not unit.indices:
        raise ValueError("Unit support must be non-empty")
    if any(i < 0 or i >= len(points) for i in unit.indices):
        raise ValueError("Unit support lies outside the observation")
    scale2 = context.observation.scale ** 2
    scores = []
    for model in context.model_family:
        residual = sum(float(model.squared_distance(points[i])) for i in unit.indices)
        score = residual / (len(unit.indices) * scale2) + float(model.complexity)
        if not isfinite(score):
            raise ValueError("Observation-derived model score must be finite")
        scores.append((model, score))
    return tuple(scores)


def M_X(unit: StructuralUnit, context) -> Tuple[object, ...]:
    """Return the local model quotient M_X(A)=argmin_{m in M(X)} F_X(A,m)+k(m)."""
    scored = unit_model_scores(unit, context)
    minimum = min(score for _, score in scored)
    return tuple(model for model, score in scored if score == minimum)


def M_X_score(unit: StructuralUnit, context) -> float:
    """Return the attained local model score for M_X(A)."""
    return min(score for _, score in unit_model_scores(unit, context))


def _local_pairwise_scale(source: StructuralUnit, target: StructuralUnit, context) -> float:
    points = context.observation.points
    indices = tuple(source.indices) + tuple(target.indices)
    distances = []
    for left in range(len(indices)):
        for right in range(left + 1, len(indices)):
            distances.append(point_distance(points[indices[left]], points[indices[right]]))
    if not distances:
        return 0.0
    ordered = sorted(distances)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return 0.5 * (ordered[middle - 1] + ordered[middle])


def Q_X(source: StructuralUnit, target: StructuralUnit, context) -> bool:
    """Strong observation-derived semantic relation predicate.

    Q_X(A,B) is true iff A and B are distinct non-empty Units and their
    minimum cross-support distance does not exceed the median pairwise
    distance of the local observation A union B.  The criterion is scale-free,
    deterministic, label-free, and invariant under observation relabeling.
    """
    if source == target or not source.indices or not target.indices:
        return False
    points = context.observation.points
    cross = min(
        point_distance(points[i], points[j])
        for i in source.indices
        for j in target.indices
    )
    local_scale = _local_pairwise_scale(source, target, context)
    return isfinite(cross) and isfinite(local_scale) and cross <= local_scale


def Q_X_strength(source: StructuralUnit, target: StructuralUnit, context) -> float:
    """Return a bounded geometric strength score for the Q_X relation."""
    if source == target or not source.indices or not target.indices:
        return 0.0
    points = context.observation.points
    cross = min(point_distance(points[i], points[j]) for i in source.indices for j in target.indices)
    scale = _local_pairwise_scale(source, target, context)
    if scale <= 0.0:
        return 1.0 if cross == 0.0 else 0.0
    return max(0.0, min(1.0, scale / (scale + cross)))


__all__ = ["M_X", "M_X_score", "Q_X", "Q_X_strength", "unit_model_scores"]
