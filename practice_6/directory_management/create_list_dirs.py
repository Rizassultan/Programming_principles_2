import os

path = "Practice6/data/documents"

os.makedirs(path, exist_ok=True)

print("Directories created.")

for item in os.listdir("Practice6"):
    print(item)