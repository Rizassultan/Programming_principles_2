class Worker:
    def work(self):
        print('work')

class Dev(Worker):
    def work(self):
        print('code')

w = Worker()
d = Dev()

w.work()
d.work()