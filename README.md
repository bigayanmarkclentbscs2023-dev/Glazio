# GlacioSim

An educational Python project inspired by the uploaded proposal:
"Simulation of Glacier Melting, Instability, and Glacial Lake Outburst Floods
Under Different Climate Scenarios."

## Requirements
- Python 3.10 or newer recommended

## Install
Open a terminal in this folder and run:

```bash
python -m pip install -r requirements.txt
```

If `python` is not recognized on Windows, try `py -m pip install -r requirements.txt`.

## Run the terminal simulation
```bash
python main.py
```

It prints scenario summaries, writes CSV files into `results/`, and opens
Matplotlib graphs.

## Run the interactive dashboard
```bash
python -m streamlit run app.py
```

## Files
- `config.py`: model parameters and synthetic scenario rates
- `glacier_model.py`: annual glacier melt, lake balance, and illustrative stability
- `stability_model.py`: toy avalanche and dam-failure event rules
- `lake_flood_model.py`: synthetic two-dimensional grid propagation
- `visualization.py`: plots
- `main.py`: terminal entry point
- `app.py`: optional Streamlit dashboard

## Scientific caution
This project is a teaching prototype, not a calibrated glaciology or hydraulic
model. Numeric parameters and event rules are illustrative. The grid is not
real terrain; values are not georeferenced flood depths. Do not use outputs for
real-world forecasting, emergency response, or hazard warnings. For a research
version, replace assumptions with documented literature-based equations and
validated datasets, test sensitivity and uncertainty, and compare against
published case studies.
