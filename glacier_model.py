"""Glacier melt and glacial lake volume model."""
import numpy as np
import pandas as pd
from config import YEARS, DEFAULTS


def simulate_glacier(warming_rate, params=None, years=YEARS):
    """Return annual synthetic glacier/lake simulation results as a DataFrame."""
    p = DEFAULTS.copy()
    if params:
        p.update(params)

    glacier = max(0.0, float(p["initial_glacier_size"]))
    lake = max(0.0, float(p["initial_lake_volume"]))
    records = []

    for year in range(years + 1):
        temperature = float(p["initial_temperature_anomaly"]) + year * warming_rate

        # Illustrative melt relationship, not a physical glacier model.
        melt_rate = max(
            0.0,
            float(p["annual_base_melt"])
            + float(p["temperature_melt_factor"]) * temperature,
        )
        melt_amount = min(glacier, melt_rate)
        glacier = max(0.0, glacier - melt_amount)

        meltwater = melt_amount * float(p["meltwater_conversion"])
        rainfall = max(0.0, float(p["annual_rainfall_inflow"]))
        outflow = lake * np.clip(float(p["lake_outflow_fraction"]), 0.0, 1.0)
        lake = max(0.0, lake + meltwater + rainfall - outflow)

        # Synthetic stress components are bounded for transparent demonstration.
        temperature_stress = np.clip(
            temperature * float(p["temperature_stress_factor"]), 0.0, 1.0
        )
        rainfall_stress = np.clip(
            rainfall * float(p["rainfall_stress_factor"]), 0.0, 1.0
        )
        lake_stress = np.clip(
            lake * float(p["lake_stress_factor"]), 0.0, 1.0
        )
        instability = float(np.clip(
            0.45 * temperature_stress
            + 0.25 * rainfall_stress
            + 0.30 * lake_stress,
            0.0, 1.0
        ))
        stability_index = 100.0 * (1.0 - instability)

        records.append({
            "Year": year,
            "Temperature Anomaly (C)": temperature,
            "Glacier Size (relative units)": glacier,
            "Melt Amount (relative units/year)": melt_amount,
            "Meltwater Inflow (million m3)": meltwater,
            "Rainfall Inflow (million m3)": rainfall,
            "Lake Outflow (million m3)": outflow,
            "Lake Volume (million m3)": lake,
            "Instability Score (0-1)": instability,
            "Stability Index (0-100)": stability_index,
        })

    return pd.DataFrame(records)
