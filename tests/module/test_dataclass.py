from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class User:
    class Address:
        country: str
        city: str

    name: str
    age: int
    address: list[Address]


def test_dataclass():
    d = {
        "name": "John Doe",
        "age": 30,
        "address": [{"country": "USA", "city": "New York"}],
    }
    user = User.from_dict(d)
    print(user)
