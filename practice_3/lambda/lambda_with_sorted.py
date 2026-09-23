# Using lambda to customize the sort key
users = [
    {'name': 'Alice', 'age': 30},
    {'name': 'Bob', 'age': 25},
    {'name': 'Charlie', 'age': 35}
]

# Sort by age (ascending)
sorted_by_age = sorted(users, key=lambda user: user['age'])

print("Users sorted by age:")
for user in sorted_by_age:
    print(user)