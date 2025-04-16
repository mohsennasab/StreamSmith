import os
from datetime import datetime


# Function to create a folder at the given path if it does not exist
def CreateFolder(path):
    if not os.path.exists(path):
        os.makedirs(path)

def log_progress(folder_path, message):
    log_file = os.path.join(folder_path, "nuhg_log.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {message}\n")