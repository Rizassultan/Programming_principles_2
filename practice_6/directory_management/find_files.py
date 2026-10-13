import os

path = input("Enter a path: ")

print("Exists:", os.path.exists(path))
print("Is file:", os.path.isfile(path))
print("Is directory:", os.path.isdir(path))