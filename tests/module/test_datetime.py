import datetime


def test_1():
    d = datetime.date(2011, 1, 12)
    print(type(d))
    res = d - datetime.timedelta(days=2)
    print(res)
    d2 = datetime.datetime.now()
    print(d2)

