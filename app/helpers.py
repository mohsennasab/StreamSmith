import os

# Function to create a folder at the given path if it does not exist
def CreateFolder(path):
    if not os.path.exists(path):
        os.makedirs(path)
