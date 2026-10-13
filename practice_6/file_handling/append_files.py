with open("sample.txt", "a", encoding="utf-8") as file:
    file.write("This line was appended.\n")

with open("sample.txt", "r", encoding="utf-8") as file:
    print(file.read())