
# Normalized Unit Hydrograph Generator

![App Screenshot](./app_screenshot.png)

## Overview

The **Normalized Unit Hydrograph Generator** is a user-friendly Streamlit-based application that enables hydrologists and water resource engineers to:

- Download USGS streamflow data
- Detect and filter peak flow events
- Analyze storm hydrographs
- Smooth hydrographs using Gaussian filters
- Generate and plot Dimensionless Unit Hydrographs (DUHs)

Developed by [Mohsen Tahmasebi Nasab, PhD](https://www.hydromohsen.com/), this tool supports peak-based hydrograph normalization workflows for any USGS streamflow site.

---

## Features

- 📥 **Automated Data Download**: Pulls historical streamflow records from USGS NWIS.
- 🏔️ **Peak Detection**: Uses prominence and time threshold filters to extract significant peak flows.
- 📊 **Hydrograph Analysis**: Allows manual review and adjustment of detected events.
- 🧪 **Gaussian Smoothing**: Cleans noisy hydrographs to better represent rainfall-runoff behavior.
- 📈 **DUH Generation**: Produces normalized, dimensionless unit hydrographs from smoothed data.

---

## How to Run

1. Clone the repo or download the code.
2. Set up your Python environment (Python ≥ 3.8 recommended).
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Launch the app:

```bash
streamlit run NormalizedHydrographGenerator.py
```

---

## Folder Structure

- `app/`
  - `data_io.py` – USGS data download and preprocessing
  - `helpers.py` – utility functions like folder creation and logging
  - `peak_detection.py` – peak identification and filtering logic
  - `plotting.py` – Matplotlib and Plotly-based visualizations
  - `smoothing.py` – hydrograph smoothing and DUH calculation
- `launch_gui.py` – optional launcher script
- `NormalizedHydrographGenerator.py` – main Streamlit interface

---

## Output Files

- `USGS_Discharge_<site>.csv` – raw downloaded streamflow data
- `Peaks_<site>_All_Years.csv` – detected peak flow events
- `Event_<n>_<year>.csv` – extracted hydrographs around selected peaks
- `S_Event_<n>.csv` – smoothed hydrograph
- `DUH_Event_<n>.csv` – dimensionless unit hydrograph
- `overall_duh.csv` – combined DUH from all events

---

## License

© 2024 Mohsen Tahmasebi Nasab. All rights reserved.
