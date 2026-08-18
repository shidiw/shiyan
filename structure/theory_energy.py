"""Theory-compliant structural energy terms.

This module is the formal bridge between the mathematical Struct3D model and
its implementation.  It deliberately does not invent additional energy
terms.  Terms that are not yet fixed by the theory are represented explicitly
as interfaces rather than silently replaced by heuristics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional

import numpy as np


@dataclass(frozen=True)
class EnergyWeights:
    """Weights for the currently specified structural compatibility terms."""

    distance: float = 1.0
    normal: float = 1.0
    curvature: float = 1.0
    boundary: float = 1.0


class TheoryStructuralEnergy:
    """Evaluate the currently specified Struct3D energy functional.

    The intended decomposition is

        E = E_fit + lambda_c * C + lambda_b * B

    with

        C = w_d D + w_n N + w_k K + w_b B_c.

    The implementation keeps the distinction between the primitive fitting
    term, compatibility terms, and boundary term explicit.  It does *not*
    substitute primitive parameter count for compatibility, nor point-spread
    variance for a graph boundary term.
    """

    def __init__(
        self,
        lambda_c: float = 1.0,
        lambda_b: float = 1.0,
        weights: Optional[EnergyWeights] = None,
    ) -> None:
        self.lambda_c = float(lambda_c)
        self.lambda_b = float(lambda_b)
        self.weights = weights or EnergyWeights()

    def compute(
        self,
        unit: Any,
        *,
        compatibility: Optional[Mapping[str, float]] = None,
        boundary: Optional[float] = None,
    ) -> dict[str, float]:
        """Compute the formal energy decomposition for one candidate unit.

        ``compatibility`` is intentionally explicit.  A caller that has not
        yet implemented a theoretically justified boundary term must pass
        ``boundary=None`` rather than silently using an unrelated statistic.
        """
        fit = float(self.fit_energy(unit))

        c = self.compatibility_energy(compatibility)
        b = 0.0 if boundary is None else float(boundary)
        total = fit + self.lambda_c * c + self.lambda_b * b

        if hasattr(unit, "energy"):
            unit.energy = total

        return {
            "total": total,
            "fit": fit,
            "compatibility": c,
            "boundary": b,
        }

    def compatibility_energy(
        self,
        compatibility: Optional[Mapping[str, float]],
    ) -> float:
        """Compute C = w_d D + w_n N + w_k K + w_b B_c.

        Missing terms are not guessed; they contribute zero until supplied by
        the corresponding theory-compliant relation implementation.
        """
        if compatibility is None:
            return 0.0
        return float(
            self.weights.distance * compatibility.get("distance", 0.0)
            + self.weights.normal * compatibility.get("normal", 0.0)
            + self.weights.curvature * compatibility.get("curvature", 0.0)
            + self.weights.boundary * compatibility.get("boundary", 0.0)
        )

    def fit_energy(self, unit: Any) -> float:
        primitive = getattr(unit, "primitive", None)
        points = np.asarray(getattr(unit, "points", []), dtype=float)
        params = getattr(unit, "parameters", {}) or {}

        if len(points) == 0:
            return 0.0
        if primitive == "plane":
            n = np.asarray(params["normal"], dtype=float)
            d = float(params["d"])
            return float(np.mean((np.abs(points @ n + d)) ** 2))
        if primitive == "sphere":
            center = np.asarray(params["center"], dtype=float)
            radius = float(params["radius"])
            residual = np.linalg.norm(points - center, axis=1) - radius
            return float(np.mean(residual**2))
        if primitive == "cylinder":
            center = np.asarray(params["center"], dtype=float)
            radius = float(params["radius"])
            residual = np.linalg.norm(points[:, :2] - center[:2], axis=1) - radius
            return float(np.mean(residual**2))
        raise ValueError(f"Unsupported primitive: {primitive!r}")
