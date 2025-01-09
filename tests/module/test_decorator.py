from functools import wraps


def singleton(cls):
    instance = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instance:
            instance[cls] = cls(*args, **kwargs)
        return instance[cls]

    return get_instance


@singleton
class A:
    pass


class B:
    pass


def test_1():
    print(A.__name__)
    print(B.__name__)
    pass
