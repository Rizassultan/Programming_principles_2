# filter() creates a list of elements for which a function returns True
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Using filter with lambda to get only even numbers
even_numbers = list(filter(lambda x: x % 2 == 0, numbers))

print(f"Original: {numbers}")
print(f"Evens:    {even_numbers}")