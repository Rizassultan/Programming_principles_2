fruits = ["Apple", "Banana", "Orange", "Mango"]

with open("fruits.txt", "w", encoding="utf-8") as file:
    for fruit in fruits:
        file.write(fruit + "\n")

print("List saved to file.")