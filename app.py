"""GlacioSim dashboard styled after the provided analytics-dashboard reference.

Run: python -m streamlit run app.py
All model values are synthetic educational outputs, not hazard forecasts.
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from config import SCENARIOS, DEFAULTS
from glacier_model import simulate_glacier
from stability_model import add_hazard_events
from lake_flood_model import simulate_flood_grid, flood_summary
from visualization import plot_flood

st.set_page_config(
    page_title="GlacioSim | Climate Analytics",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Dashboard styling inspired by the supplied reference: light background,
# compact metric cards, purple accent, fine borders and spacious chart area.
st.markdown("""
<style>
:root { --accent: #625bff; --ink: #20212a; --muted: #777987; }
.stApp { background: #fafafd; color: var(--ink); }
.block-container { max-width: 1500px; padding-top: 1.2rem; padding-bottom: 2rem; }
header[data-testid="stHeader"] { background: transparent; }
h1, h2, h3 { letter-spacing: -0.025em; }
.brand { display:flex; align-items:center; gap:10px; font-size:25px;
         font-weight:800; color:#26264b; margin: 0.25rem 0 1.25rem; }
.brand-icon { display:inline-flex; width:32px; height:32px; border-radius:10px;
              align-items:center; justify-content:center; color:white;
              background:linear-gradient(135deg,#8a82ff,#4e43e8); }
.subhead { color:#727584; font-size:14px; }
div[data-testid="stMetric"] { background:white; border:1px solid #ededf3;
  padding:15px 16px; border-radius:9px; min-height:105px;
  box-shadow:0 1px 2px rgba(25,25,45,.035); }
div[data-testid="stMetricLabel"] p { color:#777987; font-size:12px;
  font-weight:700; text-transform:uppercase; letter-spacing:.035em; }
div[data-testid="stMetricValue"] { font-size:26px; font-weight:750; color:#22232b; }
div[data-testid="stMetricDelta"] { font-size:12px; }
.panel { background:white; border:1px solid #ededf3; border-radius:10px;
         padding:17px 19px; box-shadow:0 1px 2px rgba(25,25,45,.035); }
.panel-title { font-size:14px; font-weight:750; margin-bottom:12px; color:#292a34; }
.small-note { color:#777987; font-size:12px; }
div[data-testid="stPlotlyChart"], div[data-testid="stImage"] { border-radius:8px; }
.stButton > button { border-radius:8px; border:0; background:#5145f5; color:white; }
section[data-testid="stSidebar"] { background:#f3f3f9; }
</style>
""", unsafe_allow_html=True)

# Header
head1, head2 = st.columns([7, 2])
with head1:
    st.markdown('<div class="brand"><span class="brand-icon">G</span> GlacioSim <span class="subhead">Climate & Glacier Analytics</span></div>', unsafe_allow_html=True)
with head2:
    st.caption("COMPUTATIONAL SCIENCE")
st.markdown(
    '<div class="subhead">🏔️ Himalayan glacier system &nbsp; • &nbsp; '
    '<span style="color:#12b886">●</span> Simulation engine ready</div>',
    unsafe_allow_html=True,
)
st.write("")

with st.sidebar:
    st.markdown("## ⚙️ Simulation controls")
    st.caption("Adjust the assumptions and rerun the model.")
    years = st.slider("Simulation duration (years)", 10, 100, 50, 5)
    initial_glacier = st.number_input("Initial glacier size (relative units)", min_value=1.0, max_value=1000.0, value=100.0, step=10.0)
    initial_lake = st.number_input("Initial lake volume (million m³)", min_value=0.0, max_value=1000.0, value=10.0, step=1.0)
    base_melt = st.number_input("Annual base melt", min_value=0.0, max_value=20.0, value=2.0, step=0.5)
    melt_factor = st.number_input("Temperature melt factor", min_value=0.0, max_value=10.0, value=1.5, step=0.1)
    rainfall = st.number_input("Synthetic rainfall inflow (million m³/year)", min_value=0.0, max_value=10.0, value=0.05, step=0.05, format="%.2f")
    selected_scenarios = st.multiselect("Climate scenarios", list(SCENARIOS), default=list(SCENARIOS))
    seed = st.number_input("Random seed", min_value=0, max_value=999999, value=42, step=1)
    run = st.button("Run simulation", use_container_width=True)

if not selected_scenarios:
    st.warning("Select at least one climate scenario in the sidebar.")
    st.stop()

params = DEFAULTS.copy()
params.update({
    "initial_glacier_size": initial_glacier,
    "initial_lake_volume": initial_lake,
    "annual_base_melt": base_melt,
    "temperature_melt_factor": melt_factor,
    "annual_rainfall_inflow": rainfall,
})

results = {}
for scenario in selected_scenarios:
    frame = simulate_glacier(SCENARIOS[scenario]["warming_rate"], params=params, years=years)
    frame = add_hazard_events(frame, params=params, seed=int(seed))
    results[scenario] = frame

# Headline KPIs
finals = [df.iloc[-1] for df in results.values()]
baseline = results[selected_scenarios[0]].iloc[0]
max_lake = max(float(row["Lake Volume (million m3)"]) for row in finals)
min_stability = min(float(row["Stability Index (0-100)"]) for row in finals)
max_melt = max(float(df["Melt Amount (relative units/year)"].max()) for df in results.values())
glof_count = sum(int(df["GLOF Occurred"].sum()) for df in results.values())
avalanche_count = sum(int(df["Avalanche Event"].sum()) for df in results.values())

metrics = [
    ("SCENARIOS", len(results), "Number of climate scenarios selected"),
    ("FINAL LAKE VOLUME", f"{max_lake:.1f}M m³", None),
    ("PEAK MELT RATE", f"{max_melt:.1f}", None),
    ("LOWEST STABILITY", f"{min_stability:.0f}/100", None),
    ("AVALANCHE EVENTS", avalanche_count, None),
    ("SIMULATED GLOFs", glof_count, None),
]
for start in range(0, len(metrics), 3):
    metric_columns = st.columns(3)
    for column, (label, value, help_text) in zip(metric_columns, metrics[start:start + 3]):
        column.metric(label, value, help=help_text)

st.write("")
chart_col, control_col = st.columns([2, 1])
with chart_col:
    st.markdown('<div class="panel-title">GLACIER & LAKE TRENDS</div>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(12, 4.4))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    # Glacier size on left axis; lake volume on right axis for readable comparison.
    ax2 = ax.twinx()
    colors = ["#625bff", "#19a974", "#f59e0b"]
    for i, (scenario, df) in enumerate(results.items()):
        color = colors[i % len(colors)]
        ax.plot(df["Year"], df["Glacier Size (relative units)"],
                color=color, linewidth=2.3, label=f"{scenario} — glacier")
        ax2.plot(df["Year"], df["Lake Volume (million m3)"],
                 color=color, linewidth=1.8, linestyle="--", alpha=.75,
                 label=f"{scenario} — lake")
    ax.set_xlabel("Simulation year", color="#777987")
    ax.set_ylabel("Glacier size (relative units)", color="#777987")
    ax2.set_ylabel("Lake volume (million m³)", color="#777987")
    ax.grid(axis="y", color="#ececf3", linewidth=1)
    ax.spines[["top", "right"]].set_visible(False)
    ax2.spines[["top", "left"]].set_visible(False)
    ax.tick_params(colors="#777987")
    ax2.tick_params(colors="#777987")
    handles1, labels1 = ax.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(handles1 + handles2, labels1 + labels2, loc="upper center",
              bbox_to_anchor=(0.5, -0.18), ncol=3, frameon=False, fontsize=8)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
with control_col:
    with st.container(border=True):
        st.markdown('<div class="panel-title">MODEL STATUS</div>', unsafe_allow_html=True)
        st.markdown("**Climate scenarios**")
        for name in selected_scenarios:
            st.write(f"🟣 {name}")
        st.divider()
        st.markdown("**Run configuration**")
        st.write(f"Duration: **{years} years**")
        st.write(f"Random seed: **{seed}**")
        st.write(f"Rainfall input: **{rainfall:.2f}**")
        st.caption("Scenario rates are illustrative assumptions.")

st.write("")
left, right = st.columns(2)
with left:
    st.markdown('<div class="panel-title">SCENARIO SUMMARY</div>', unsafe_allow_html=True)
    summary_rows = []
    for name, df in results.items():
        final = df.iloc[-1]
        summary_rows.append({
            "Scenario": name,
            "Final glacier": round(float(final["Glacier Size (relative units)"]), 2),
            "Lake volume (M m³)": round(float(final["Lake Volume (million m3)"]), 2),
            "Stability / 100": round(float(final["Stability Index (0-100)"]), 1),
            "Avalanche": "Yes" if df["Avalanche Event"].any() else "No",
            "GLOF": "Yes" if df["GLOF Occurred"].any() else "No",
        })
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)
    choice = st.selectbox("Inspect annual results", selected_scenarios)
    csv = results[choice].to_csv(index=False).encode("utf-8")
    st.download_button("Download scenario CSV", csv, f"{choice.lower().replace(' ', '_')}.csv", "text/csv")

with right:
    st.markdown('<div class="panel-title">FLOOD PROPAGATION GRID</div>', unsafe_allow_html=True)
    choice_df = results[choice]
    event_rows = choice_df[choice_df["GLOF Occurred"]]
    if not event_rows.empty:
        release = float(event_rows.iloc[0]["GLOF Release (million m3)"])
        st.caption(f"Illustrative release from simulated event: {release:.2f} million m³")
    else:
        st.caption("No dam failure in this run; showing a small illustrative flood-grid example.")
        release = 1.0
    _, depth, _ = simulate_flood_grid(release, params=params, seed=int(seed))
    sm = flood_summary(depth)
    a, b, c = st.columns(3)
    a.metric("Flooded cells", sm["Flooded grid cells"])
    b.metric("Max relative depth", f"{sm['Maximum relative depth']:.3f}")
    c.metric("Grid affected", f"{sm['Flooded fraction (%)']:.1f}%")
    flood_fig = plot_flood(depth)
    st.pyplot(flood_fig, use_container_width=True)
    plt.close(flood_fig)

st.markdown("---")
st.caption(
    "GlacioSim is an educational computational model. All values, thresholds, "
    "event probabilities, and grid depths are simplified assumptions; outputs "
    "are not real-world glacier forecasts, flood maps, or emergency warnings."
)
