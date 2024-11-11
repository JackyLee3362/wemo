from __future__ import annotations

# 2024-10-26


class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, value: Person):
        return self.name == value.name

    def __repr__(self):
        return f"Person({self.name}, {self.age})"


def test_person():
    s1 = [Person("a", 1), Person("b", 2)]
    s2 = [Person("a", 100), Person("b", 2), Person("c", 3)]

    d1 = {u.__hash__(): u for u in s1}
    d2 = {u.__hash__(): u for u in s2}
    keys = d2.keys() - d1.keys()
    print("key差值", keys)
    for k in keys:
        print(k, d2[k])
    print("item差值", d2.items() - d1.items())


def test_2():
    v = {"abc"}
    print("----------")
    print("type:", type(v))
    print("value:", v)


def test_3():
    print("test_3")
    print(__name__)


def test_4():
    print("test_4")
    d = {"a": 1}
    print(d.get("b"))
