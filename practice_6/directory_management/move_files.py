import os
import shutil

source = "Practice6/source"
destination = "Practice6/destination"

os.makedirs(destination, exist_ok=True)

filename = "sample.txt"
source_path = os.path.join(source, filename)
destination_path = os.path.join(destination, filename)

if os.path.isfile(source_path):
    shutil.copy2(source_path, destination_path)
    print("File copied.")
else:
    print("Source file not found.")