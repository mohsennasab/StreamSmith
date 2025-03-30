import subprocess
import os

# Optional: Set the working directory if needed
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Run the Streamlit app on port 8502
subprocess.run(["streamlit", "run", "NormalizedHydrographGenerator.py", "--server.port", "8502"])
