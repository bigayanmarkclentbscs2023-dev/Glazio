"""Plotting helpers for GlacioSim."""
import matplotlib.pyplot as plt


def plot_scenarios(results):
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    metrics = [
        ("Glacier Size (relative units)", "Simulated glacier size"),
        ("Lake Volume (million m3)", "Simulated lake volume"),
        ("Stability Index (0-100)", "Illustrative stability index"),
        ("Synthetic Avalanche Probability (%)", "Synthetic avalanche probability"),
    ]

    for ax, (column, title) in zip(axes.flat, metrics):
        for scenario, df in results.items():
            ax.plot(df["Year"], df[column], label=scenario)
        ax.set_title(title)
        ax.set_xlabel("Simulation year")
        ax.grid(True, alpha=0.3)
        ax.legend()

    fig.suptitle("GlacioSim — climate scenario comparison", fontsize=15)
    fig.tight_layout()
    return fig


def plot_flood(depth, terrain=None):
    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(depth, origin="upper", cmap="Blues")
    ax.set_title("Synthetic 2-D flood depth grid")
    ax.set_xlabel("Grid column (not real longitude)")
    ax.set_ylabel("Grid row (not real latitude)")
    fig.colorbar(im, ax=ax, label="Relative water depth")
    fig.tight_layout()
    return fig
