from time import sleep


def is_windows():
    # This sleep could be some complex operation instead
    sleep(5)
    return True


def get_operating_system():
    return "Windows" if is_windows() else "Linux"


def test_get_operation_system(mocker):
    mocker.patch("test_pytest_mock.is_windows", return_value=True)
    res = get_operating_system()
    print(res)


def test_get_operation_system_2(mocker):
    mocker.patch("test_pytest_mock.get_operating_system", return_value="Linux")
    res = get_operating_system()
    print(res)


class Person:
    def __init__(self, name):
        self.name = name
        pass

    def say(self):
        return "hello, {}".format(self.name)


def test_person(mocker):
    mocker.patch("test_pytest_mock.Person.say", return_value="hello, Jack")
    p = Person("Tom")
    res = p.say()
    print(res)
