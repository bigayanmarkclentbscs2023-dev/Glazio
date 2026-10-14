"""Run GlacioSim from the terminal."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

from config import SCENARIOS, DEFAULTS, RANDOM_SEED
from glacier_model import simulate_glacier
from stability_model import add_hazard_events
from lake_flood_model import simulate_flood_grid, flood_summary
from visualization import plot_scenarios, plot_flood


def run_simulation(years=50, params=None, seed=RANDOM_SEED):
    results = {}
    for scenario, config in SCENARIOS.items():
        df = simulate_glacier(config["warming_rate"], params=params, years=years)
        df = add_hazard_events(df, params=params, seed=seed)
        results[scenario] = df
    return results


def main():
    output = Path("results")
    output.mkdir(exist_ok=True)

    results = run_simulation()

    print("\\nGLACIOSIM — EDUCATIONAL SIMULATION")
    print("All values are synthetic and are not real-world forecasts.\\n")

    for scenario, df in results.items():
        df.to_csv(output / f"{scenario.lower().replace(' ', '_')}.csv", index=False)
        final = df.iloc[-1]
        print(f"Scenario: {scenario}")
        print(f"  Final glacier size: {final['Glacier Size (relative units)']:.2f}")
        print(f"  Final lake volume: {final['Lake Volume (million m3)']:.2f} million m3")
        print(f"  Final stability index: {final['Stability Index (0-100)']:.2f}/100")

        avalanche_years = df.loc[df["Avalanche Event"], "Year"].tolist()
        glof_years = df.loc[df["GLOF Occurred"], "Year"].tolist()
        print(f"  Simulated avalanche year(s): {avalanche_years or 'None'}")
        print(f"  Simulated GLOF year(s): {glof_years or 'None'}")
        print()

    # Use the first simulated GLOF among scenarios for the grid demo.
    release = 0.0
    selected = None
    for scenario, df in results.items():
        events = df[df["GLOF Occurred"]]
        if not events.empty:
            release = float(events.iloc[0]["GLOF Release (million m3)"])
            selected = scenario
            break

    if release > 0:
        _, depth, _ = simulate_flood_grid(release, params=DEFAULTS, seed=seed)
        print(f"Flood grid demo uses {selected}, release={release:.2f} million m3")
    else:
        # Demonstrate the grid visualization even when the toy event rules
        # produce no dam failure in a run.
        _, depth, _ = simulate_flood_grid(1.0, params=DEFAULTS, seed=seed)
        print("No simulated GLOF event occurred; showing a small illustrative grid demo.")

    print("Flood grid summary:", flood_summary(depth))
    plot_scenarios(results)
    plot_flood(depth)
    plt.show()


if __name__ == "__main__":
    main()
