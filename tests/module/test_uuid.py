import uuid


def test_uuid():
    print(uuid.uuid3(namespace=uuid.NAMESPACE_DNS, name="1"))
