<p align="center">
  <img src="Images/Logo.png" alt="StreamSmith Logo" width="250"/>
</p>

# StreamSmith

StreamSmith is a Streamlit-based web application for hydrologists, engineers, and educators to generate and analyze **Normalized Unit Hydrographs (NUH)** using USGS streamflow data.

---

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Launching the App](#launching-the-app)
- [Example Use Cases](#example-use-cases)
- [Contributing](#contributing)
- [License](#license)

---

## 🚀 Features

- 📥 Download discharge data from USGS NWIS
- 📊 Detect and filter streamflow peaks
- 📈 Visualize hydrographs and peak flow events
- 🧮 Create and export smoothed & normalized unit hydrographs
- 📁 Save hydrograph events and DUHs in organized folders
- ✨ Pixi environment support for reproducible installs

---

## ⚙️ Installation

This app uses [Pixi](https://pixi.sh/latest/) for environment management.

1. Install Pixi (if you haven’t):
   ```bash
   curl -sSL https://pixi.sh/install.sh | bash
   ```

2. Navigate to the NUH project folder and install dependencies:
   ```bash
   cd NUH
   pixi install
   ```

---

## ▶️ Launching the App

After installation, run the app with:

```bash
pixi run streamlit run NormalizedHydrographGenerator.py
```

---

## 📁 Project Structure

```
StreamSmith/
├── app/
│   ├── data_io.py
│   ├── helpers.py
│   ├── peak_detection.py
│   ├── plotting.py
│   └── smoothing.py
├── Images/
│   └── Logo.png
├── NormalizedHydrographGenerator.py
├── launch_gui.py
├── README.md
├── pixi.toml
├── pixi.lock

```

## 📦 Example Use Cases

- Analyze seasonal flood events from historical streamflow records.
- Generate normalized hydrographs for rainfall-runoff modeling.
- Study regional differences in stormflow responses.
- Support academic research and watershed planning workflows.

---

## 🤝 Contributing

Feel free to fork the repo and submit pull requests. Open an issue if you spot bugs or want to suggest features!

---

## 📄 License

This project is licensed under the MIT License.

---

**Developed by:** Mohsen Tahmasebi Nasab, PhD  
🌐 [hydromohsen.com](https://www.hydromohsen.com)


---
