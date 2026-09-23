class Animal:
    def __init__(self, name):
        self.name = name

    def eat(self):
        print('eat')

class Cat(Animal):
    def meow(self):
        print('meow')

c = Cat('tom')
c.eat()
c.meow()