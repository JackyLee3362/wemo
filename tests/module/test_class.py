class Person:
    name = "Student"
    age: int

    def __init__(self):
        pass


def test_1():
    p = Person()
    print("----------")
    print(p.name)  # 找不到会找类属性
    print(Person.name)
    p.name = "123xxx"
    print(p.name)  # 屏蔽类属性
    print(Person.name)
    print(Person.__name__)
    try:
        age = p.age
    except AttributeError:
        age = 123
    print(age)
