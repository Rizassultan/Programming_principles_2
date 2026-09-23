class User:
    def __init__(self, u, e):
        self.u = u
        self.e = e

u1 = User('jon', 'j@a.com')
print(u1.u, u1.e)