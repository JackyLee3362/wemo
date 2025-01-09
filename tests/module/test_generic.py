import typing

T = typing.TypeVar("T")


class Student(typing.Generic[T]):
    def __init__(self):
        self.list: typing.List[T] = []


def test_1():
    s = Student[str]()
    print(s.list)
