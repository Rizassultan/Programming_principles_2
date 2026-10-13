import os

path = input("Enter a directory path: ")

if os.path.isdir(path):
    items = os.listdir(path)

    print("Directories:")
    for item in items:
        if os.path.isdir(os.path.join(path, item)):
            print(item)

    print("\nFiles:")
    for item in items:
        if os.path.isfile(os.path.join(path, item)):
            print(item)

    print("\nAll items:")
    for item in items:
        print(item)
else:
    print("Invalid directory.")