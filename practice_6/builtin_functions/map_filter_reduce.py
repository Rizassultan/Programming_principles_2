from functools import reduce

numbers = [1, 2, 3, 4, 5, 6]

# map(): double every number
doubled = list(map(lambda x: x * 2, numbers))
print("Doubled:", doubled)

# filter(): keep only even numbers
evens = list(filter(lambda x: x % 2 == 0, numbers))
print("Even numbers:", evens)

# reduce(): calculate the sum
total = reduce(lambda x, y: x + y, numbers)
print("Sum:", total)