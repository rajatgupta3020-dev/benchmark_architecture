from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class BenchmarkMetrics:
    r_squared: float
    tracking_error: float
    information_ratio: float
    active_return: float
    beta: float
    alpha: float
    score: int
    fit_band: str


def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    clean = {k: max(float(v), 0.0) for k, v in weights.items()}
    total = sum(clean.values())
    if total <= 0:
        raise ValueError("At least one benchmark component must have a positive weight.")
    return {k: v / total for k, v in clean.items()}


def make_benchmark_returns(index_returns: pd.DataFrame, weights: Dict[str, float]) -> pd.Series:
    """Create a weighted benchmark return series from component index returns."""
    normalized = normalize_weights(weights)
    missing = [name for name in normalized if name not in index_returns.columns]
    if missing:
        raise KeyError(f"Benchmark components not found: {', '.join(missing)}")
    return index_returns[list(normalized)].mul(pd.Series(normalized)).sum(axis=1)


def _r_squared(y: pd.Series, x: pd.Series) -> float:
    yv = np.asarray(y, dtype=float)
    xv = np.asarray(x, dtype=float)
    if len(yv) < 2 or np.isclose(np.std(xv), 0.0) or np.isclose(np.std(yv), 0.0):
        return 0.0
    r = float(np.corrcoef(yv, xv)[0, 1])
    if not np.isfinite(r):
        return 0.0
    return float(np.clip(r * r, 0.0, 1.0))


def calculate_metrics(portfolio: pd.Series, benchmark: pd.Series) -> BenchmarkMetrics:
    """Calculate beginner-friendly performance measurement statistics."""
    data = pd.concat([portfolio, benchmark], axis=1).dropna()
    if len(data) < 2:
        raise ValueError("At least two matching return observations are required.")

    p = data.iloc[:, 0].astype(float)
    b = data.iloc[:, 1].astype(float)
    active = p - b

    r2 = _r_squared(p, b)
    tracking_error = float(active.std(ddof=1) * np.sqrt(12))
    active_return = float((p.mean() - b.mean()) * 12)

    if tracking_error > 1e-12:
        information_ratio = active_return / tracking_error
    else:
        information_ratio = 0.0

    b_var = float(b.var(ddof=1))
    beta = float(p.cov(b) / b_var) if b_var > 1e-12 else 0.0

    # Simple single-factor regression: Portfolio = alpha + beta * Benchmark + error.
    alpha_monthly = float(p.mean() - beta * b.mean())
    alpha = alpha_monthly * 12

    score = benchmark_score(r2, tracking_error, beta)
    fit_band = quality_band(r2, tracking_error, abs(beta - 1.0))

    return BenchmarkMetrics(
        r_squared=r2,
        tracking_error=tracking_error,
        information_ratio=information_ratio,
        active_return=active_return,
        beta=beta,
        alpha=alpha,
        score=score,
        fit_band=fit_band,
    )


def _scale_lower_better(value: float, best: float, worst: float) -> float:
    if value <= best:
        return 1.0
    if value >= worst:
        return 0.0
    return (worst - value) / (worst - best)


def benchmark_score(r2: float, tracking_error: float, beta: float) -> int:
    """MVP score: 1,000 points using fit, error and exposure alignment."""
    r2_points = 400.0 * np.clip(r2, 0.0, 1.0)
    te_points = 300.0 * _scale_lower_better(tracking_error, 0.01, 0.08)
    beta_points = 300.0 * _scale_lower_better(abs(beta - 1.0), 0.0, 0.35)
    return int(round(r2_points + te_points + beta_points))


def quality_band(r2: float, tracking_error: float, beta_gap: float) -> str:
    if r2 >= 0.90 and tracking_error <= 0.02 and beta_gap <= 0.10:
        return "Excellent fit"
    if r2 >= 0.75 and tracking_error <= 0.04:
        return "Good fit"
    if r2 >= 0.50:
        return "Needs improvement"
    return "Poor fit"


def exposure_match(portfolio_exposure: Dict[str, float], benchmark_exposure: Dict[str, float]) -> float:
    """0-100 score based on absolute exposure gaps across comparable dimensions."""
    keys: Iterable[str] = set(portfolio_exposure) | set(benchmark_exposure)
    gap = sum(abs(float(portfolio_exposure.get(k, 0.0)) - float(benchmark_exposure.get(k, 0.0))) for k in keys)
    return float(np.clip(100.0 - 100.0 * gap / 2.0, 0.0, 100.0))
