"""A simple 2-D toy flood-grid visualization model.

This is a diffusion-style teaching demonstration, not a hydraulic solver.
Grid values are relative depth units and are not geographic predictions.
"""
import numpy as np
from config import GRID_ROWS, GRID_COLS, DEFAULTS


def create_terrain(rows=GRID_ROWS, cols=GRID_COLS, seed=42):
    """Create a synthetic downhill terrain with gentle deterministic variation."""
    rng = np.random.default_rng(seed)
    x = np.linspace(0.0, 1.0, cols)[None, :]
    y = np.linspace(0.0, 1.0, rows)[:, None]
    terrain = 100.0 - 55.0 * x - 8.0 * y
    terrain += rng.normal(0.0, 0.5, size=(rows, cols))
    return terrain


def simulate_flood_grid(release_volume, rows=GRID_ROWS, cols=GRID_COLS,
                        steps=None, params=None, seed=42):
    """Return synthetic terrain, final depth grid, and all time frames."""
    p = DEFAULTS.copy()
    if params:
        p.update(params)
    if steps is None:
        steps = int(p["flood_steps"])

    terrain = create_terrain(rows, cols, seed)
    depth = np.zeros((rows, cols), dtype=float)

    if release_volume <= 0:
        return terrain, depth, [depth.copy()]

    # Place the lake outlet near the upper-left edge.
    depth[2:5, 2:5] = float(p["flood_initial_depth"]) * min(
        1.0, float(release_volume) / 10.0
    )
    frames = [depth.copy()]
    diffusion = float(np.clip(p["flood_diffusion"], 0.0, 0.24))
    decay = float(np.clip(p["flood_decay"], 0.0, 0.2))

    for _ in range(int(steps)):
        old = depth
        padded = np.pad(old, 1, mode="constant")
        up = padded[:-2, 1:-1]
        down = padded[2:, 1:-1]
        left = padded[1:-1, :-2]
        right = padded[1:-1, 2:]

        # Spread water to neighboring cells; slope biases flow to the right.
        neighbor_mean = (up + down + left + right) / 4.0
        slope_bias = np.zeros_like(old)
        slope_bias[:, 1:] = np.maximum(old[:, :-1] - old[:, 1:], 0.0) * 0.08
        depth = np.maximum(
            0.0,
            old + diffusion * (neighbor_mean - old)
            + slope_bias - decay * old
        )
        frames.append(depth.copy())

    return terrain, depth, frames


def flood_summary(depth, threshold=0.05):
    """Summarize cells above an illustrative depth threshold."""
    flooded = depth > threshold
    return {
        "Flooded grid cells": int(flooded.sum()),
        "Maximum relative depth": float(depth.max()) if depth.size else 0.0,
        "Grid cells": int(depth.size),
        "Flooded fraction (%)": float(100.0 * flooded.mean()) if depth.size else 0.0,
    }
