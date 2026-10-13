import string
import os

folder = "alphabet_files"
os.makedirs(folder, exist_ok=True)

for letter in string.ascii_uppercase:
    path = os.path.join(folder, letter + ".txt")

    with open(path, "w", encoding="utf-8") as file:
        file.write(f"This is {letter}.txt\n")

print("26 files created.")