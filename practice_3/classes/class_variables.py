class Emp:
    corp = 'tech'

    def __init__(self, name):
        self.name = name

e1 = Emp('jon')
e2 = Emp('amy')

print(e1.name, e1.corp)
print(e2.name, e2.corp)

Emp.corp = 'new'
print(e1.name, e1.corp)