def name(first, last):
    return f"{first} {last}"

def data(user):
    return user, f"{user}@a.com", True

n = name('bob', 'lee')
print(n)

u, e, a = data('jon')
print(u, e, a)