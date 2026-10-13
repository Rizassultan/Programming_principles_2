names = ["Ali", "John", "Sara"]
scores = [85, 92, 78]

print("Using enumerate:")
for index, name in enumerate(names, start=1):
    print(index, name)

print("\nUsing zip:")
for name, score in zip(names, scores):
    print(name, score)

print("\nType checking:")
value = "123"

print(type(value))
print(isinstance(value, str))

number = int(value)
print(number, type(number))