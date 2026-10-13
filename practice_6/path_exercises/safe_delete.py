import os

path = input("Enter the file path to delete: ")

if not os.path.exists(path):
    print("Path does not exist.")
elif not os.path.isfile(path):
    print("The path is not a file.")
elif not os.access(path, os.W_OK):
    print("File is not writable.")
else:
    confirm = input("Are you sure you want to delete it? (yes/no): ")

    if confirm.lower() == "yes":
        try:
            os.remove(path)
            print("File deleted successfully.")
        except OSError as error:
            print("Could not delete file:", error)
    else:
        print("Deletion cancelled.")