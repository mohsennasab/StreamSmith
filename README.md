<p align="center">
  <img src="Images/Logo.png" alt="StreamSmith Logo" width="250"/>
</p>

# StreamSmith

StreamSmith is a Streamlit-based web application for hydrologists, engineers, and educators to generate and analyze **Normalized Unit Hydrographs (NUH)** using USGS streamflow data.

---

## 🚀 Features

- 📥 Download discharge data from USGS NWIS
- 📊 Detect and filter streamflow peaks
- 📈 Visualize hydrographs and peak flow events
- 🧮 Create and export smoothed & normalized unit hydrographs
- 📁 Save hydrograph events and DUHs in organized folders
- ✨ Pixi environment support for reproducible installs

---

## 🎥 What It Does (Demo Video)

📺 *Watch a quick demo of StreamSmith in action:*  

[![Watch the video](https://img.youtube.com/vi/j-TWeX9TdM8/0.jpg)](https://youtu.be/j-TWeX9TdM8?si=hdp8Zt371DRq3kdQ)

---


## ⚙️ Installation

This app uses [Pixi](https://pixi.sh/latest/) for environment management.

1. To install pixi you can run the following command in your Windows PowerShell terminal:
   ```bash
   powershell -ExecutionPolicy ByPass -c "irm -useb https://pixi.sh/install.ps1 | iex"
   ```
The above invocation will automatically download the latest version of pixi, extract it, and move the pixi binary to LocalAppData/pixi/bin. The command will also add LocalAppData/pixi/bin to your PATH environment variable, allowing you to invoke pixi from anywhere.


2. Navigate to the NUH project folder and install dependencies:
   ```bash
      cd "Project Folder"
   ```

   ```bash
   pixi install
   ```

---

## ▶️ Launching the App

After installation, run the app with:

```bash
pixi run streamlit run NormalizedHydrographGenerator.py --server.port 8502
```

---

## 🛠️ Installation Guide (Video)

💡 *Need help getting started? Follow this installation tutorial:*  

[![Watch the video](https://img.youtube.com/vi/7s881nEHuko/0.jpg)](https://youtu.be/7s881nEHuko?si=CViCl8uZcA11IbRe)

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
---

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
