class Bank:
    def __init__(self, name, bal=0):
        self.name = name
        self.bal = bal

    def add(self, amt):
        self.bal += amt
        print(self.bal)

    def sub(self, amt):
        if amt <= self.bal:
            self.bal -= amt
            print(self.bal)
        else:
            print('no funds')

b = Bank('ali', 100)
b.add(50)
b.sub(30)