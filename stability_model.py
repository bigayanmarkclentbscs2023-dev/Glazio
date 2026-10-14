"""Synthetic avalanche and moraine-dam event rules."""
import numpy as np
from config import DEFAULTS


def add_hazard_events(df, params=None, seed=42):
    """Add event flags using documented toy rules; not a real forecast."""
    p = DEFAULTS.copy()
    if params:
        p.update(params)

    rng = np.random.default_rng(seed)
    result = df.copy()
    threshold = float(p["avalanche_threshold"])
    scores = result["Instability Score (0-1)"].to_numpy()

    # A synthetic event chance rises above the selected instability threshold.
    event_probability = np.clip(
        np.maximum(0.0, scores - threshold) / max(1e-9, 1.0 - threshold),
        0.0, 0.85
    )
    # One event at most: keeps the event chain easy to inspect.
    avalanche_flags = np.zeros(len(result), dtype=bool)
    for i, chance in enumerate(event_probability):
        if rng.random() < chance:
            avalanche_flags[i] = True
            break

    result["Synthetic Avalanche Probability (%)"] = event_probability * 100.0
    result["Avalanche Event"] = avalanche_flags

    displacement = np.zeros(len(result))
    dam_stress = np.clip(
        0.45 * scores
        + 0.35 * np.clip(
            result["Lake Volume (million m3)"].to_numpy() / 100.0, 0.0, 1.0
        )
        + 0.20 * np.clip(
            result["Temperature Anomaly (C)"].to_numpy() / 5.0, 0.0, 1.0
        ),
        0.0, 1.0
    )
    dam_failure = np.zeros(len(result), dtype=bool)

    event_indices = np.flatnonzero(avalanche_flags)
    if len(event_indices):
        idx = int(event_indices[0])
        displacement[idx] = (
            result.iloc[idx]["Lake Volume (million m3)"]
            * float(p["avalanche_displacement_fraction"])
        )
        # Avalanche increases synthetic dam stress in this simplified model.
        dam_stress[idx:] = np.clip(
            dam_stress[idx:] + 0.25, 0.0, 1.0
        )
        failure_chance = np.clip(
            (dam_stress - float(p["dam_failure_threshold"])) /
            max(1e-9, 1.0 - float(p["dam_failure_threshold"])),
            0.0, 0.95
        )
        for j in range(idx, len(result)):
            if rng.random() < failure_chance[j]:
                dam_failure[j] = True
                break

    result["Avalanche Displacement (million m3)"] = displacement
    result["Dam Stress (0-1)"] = dam_stress
    result["Dam Failure"] = dam_failure
    result["GLOF Occurred"] = dam_failure
    result["GLOF Release (million m3)"] = np.where(
        dam_failure,
        result["Lake Volume (million m3)"].to_numpy()
        * float(p["dam_release_fraction"]),
        0.0
    )
    return result
