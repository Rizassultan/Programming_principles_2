class Fly:
    def fly(self):
        print('fly')

class Swim:
    def swim(self):
        print('swim')

class Fish(Fly, Swim):
    pass

f = Fish()
f.swim()
f.fly()