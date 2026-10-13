with open("sample.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

print("Number of lines:", len(lines))