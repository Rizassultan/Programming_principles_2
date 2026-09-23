# map() applies a function to all items in an iterable
numbers = [1, 2, 3, 4, 5]

# Using map with lambda to square each number
squared_numbers = list(map(lambda x: x ** 2, numbers))

print(f"Original: {numbers}")
print(f"Squared:  {squared_numbers}")