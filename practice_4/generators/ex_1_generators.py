def squares(n):
    for i in range(n + 1):
        yield i ** 2


for x in squares(5):
    print(x)