class Person:
    name = "Student"

    def __init__(self):
        pass


def test_1():
    p = Person()
    print("----------")
    print(p.name)  # 找不到会找类属性
    print(Person.name)
    p.name = "123xxx"
    print(p.name) # 屏蔽类属性
    print(Person.name)
