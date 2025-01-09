import hashlib


def test_1():
    content = b"01" * 1024
    md5 = hashlib.md5(content)
    print(md5.hexdigest())
