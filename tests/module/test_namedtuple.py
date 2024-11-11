from collections import namedtuple


def test_1():
    Point = namedtuple("Point123", ["x", "y"])
    print(type(Point))
    p = Point(x=1, y=2)
    print(type(p))
