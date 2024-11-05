class Person:
    count = 0

    def __init__(self):
        pass


def test_1():
    Person.count = 1000000
    p1 = Person()
    p1.count = 1000
    print(p1.count)
    print(Person.count)
