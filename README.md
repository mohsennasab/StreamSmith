# Normalized Hydrograph Generator (NUHG)

This interactive Streamlit app allows hydrologists and water resources engineers to generate **normalized unit hydrographs** from USGS streamflow data using peak detection, Gaussian smoothing, and interpolation techniques.

Developed by [Mohsen Tahmasebi, PhD](https://www.hydromohsen.com/)

---

## 🚀 Features

- Download daily or sub-daily USGS streamflow data
- Filter and visualize peaks for selected months
- Generate storm hydrographs and perform Gaussian smoothing
- Create and save **Dimensionless Unit Hydrographs (DUH)**
- Interpolate and aggregate DUHs across events

---

## 📦 Project Structure

```
NUHG/
├── app/                            # Modularized backend logic
│   ├── data_io.py
│   ├── helpers.py
│   ├── plotting.py
│   ├── peak_detection.py
│   ├── smoothing.py
│   └── __init__.py
├── NormalizedHydrographGenerator.py  # Streamlit GUI app
├── launch_gui.py                     # Script to launch the app
├── pixi.toml / pixi.lock             # Pixi environment files
├── .gitignore / .gitattributes
```

---

## 🧪 How to Run

1. Make sure you have [Pixi](https://prefix.dev/docs/pixi/overview) installed and your environment set up.

2. Add required packages using:

   ```bash
   pixi add streamlit pandas hydrofunctions scipy matplotlib plotly numpy
   ```

3. Run the app:

   ```bash
   python launch_gui.py
   ```

> The app will open at [http://localhost:8502](http://localhost:8502)

---

## 💡 Notes

- This tool generates **normalized hydrographs**, not true unit hydrographs (since rainfall excess data is not included).
- Gaussian smoothing and peak detection settings are fully adjustable in the interface.

---

## 📬 Contact

Questions, ideas, or suggestions?  
Reach out at [mohsennasab.com](https://www.hydromohsen.com/) or submit an issue on GitHub.

---

## 📝 License

MIT License (or specify your preferred license here)