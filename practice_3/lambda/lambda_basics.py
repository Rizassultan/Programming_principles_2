# A standard function
def add(x, y):
    return x + y

# The equivalent lambda (anonymous) function
add_lambda = lambda x, y: x + y

print(f"Standard function result: {add(5, 3)}")
print(f"Lambda function result: {add_lambda(5, 3)}")