import shutil
import os

source = "sample.txt"
backup = "sample_backup.txt"

if os.path.isfile(source):
    shutil.copy2(source, backup)
    print("Backup created.")

    confirm = input("Delete the original file? (yes/no): ")

    if confirm.lower() == "yes":
        os.remove(source)
        print("Original file deleted.")
else:
    print("Source file does not exist.")