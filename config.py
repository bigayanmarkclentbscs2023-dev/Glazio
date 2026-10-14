"""GlacioSim configuration.

All default values are illustrative assumptions for educational simulation,
not calibrated measurements or real-world hazard thresholds.
"""

YEARS = 50
GRID_ROWS = 60
GRID_COLS = 80
RANDOM_SEED = 42

SCENARIOS = {
    "Low warming": {"warming_rate": 0.02},
    "Moderate warming": {"warming_rate": 0.04},
    "High warming": {"warming_rate": 0.06},
}

DEFAULTS = {
    "initial_glacier_size": 100.0,       # relative units
    "initial_lake_volume": 10.0,         # million m^3
    "initial_temperature_anomaly": 0.0,   # degrees C
    "annual_base_melt": 2.0,             # relative units/year
    "temperature_melt_factor": 1.5,      # relative units/year/degree C
    "meltwater_conversion": 0.02,         # million m^3 per relative melt unit
    "annual_rainfall_inflow": 0.05,       # million m^3/year (synthetic)
    "lake_outflow_fraction": 0.01,        # fraction of lake volume/year
    "rainfall_stress_factor": 0.3,
    "temperature_stress_factor": 0.08,
    "lake_stress_factor": 0.005,
    "avalanche_threshold": 0.35,          # synthetic instability score threshold
    "dam_failure_threshold": 0.75,        # synthetic dam stress threshold
    "avalanche_displacement_fraction": 0.08,
    "dam_release_fraction": 0.35,
    "flood_initial_depth": 1.5,           # synthetic grid depth
    "flood_diffusion": 0.18,
    "flood_decay": 0.015,
    "flood_steps": 45,
}
