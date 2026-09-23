class Car:
    def __init__(self, make):
        self.make = make

class EV(Car):
    def __init__(self, make, bat):
        super().__init__(make)
        self.bat = bat

    def show(self):
        print(self.make, self.bat)

t = EV('tesla', 100)
t.show()