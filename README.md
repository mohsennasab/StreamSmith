
# Normalized Unit Hydrograph Generator

This Streamlit app helps users create normalized unit hydrographs using USGS streamflow data. The app allows you to:
- Download and filter data from USGS gages
- Detect and refine streamflow peaks
- Generate and export storm hydrographs
- Apply Gaussian smoothing
- Create and visualize Dimensionless Unit Hydrographs (DUHs)

## 📦 Environment Setup (using Pixi)

This project uses [Pixi](https://prefix.dev/docs/pixi) for environment management and reproducibility.

### 1. Install Pixi
If you don't have Pixi installed yet:

```bash
curl -sSL https://install.pixi.sh | bash
```

### 2. Create and activate the environment

```bash
pixi install
pixi run start
```

This will install all dependencies and launch the app.

## ▶️ Running the App

Once the environment is ready, run the Streamlit app:

```bash
pixi run start
```

Or manually:

```bash
streamlit run NormalizedHydrographGenerator.py
```

## 📁 Project Structure

```
NUH/
├── app/
│   ├── data_io.py
│   ├── helpers.py
│   ├── peak_detection.py
│   ├── plotting.py
│   └── smoothing.py
├── NormalizedHydrographGenerator.py
├── launch_gui.py
├── README.md
├── pixi.toml
├── pixi.lock
```

## 📋 Features

- Streamlit-based user interface
- Prominence-based peak detection with time gap filtering
- Manual peak filtering through index selection
- Logging of all major actions and steps
- Gaussian smoothing and DUH creation
- All outputs saved in a structured directory per gage

## 🧪 Example Usage

1. Input a USGS site number and date range.
2. Select desired months for peak analysis.
3. Choose a prominence value (e.g., discharge std dev).
4. Detect and optionally filter peaks.
5. Process, smooth, and normalize hydrographs.
6. Download resulting DUHs and view plots.

## 📄 License

This project is for educational and research purposes. Contact the developer for extended use or publication.

---

**Developed by:** Mohsen Tahmasebi, PhD  
🌐 [hydromohsen.com](https://www.hydromohsen.com)
