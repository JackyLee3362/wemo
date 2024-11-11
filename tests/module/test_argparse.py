import argparse


def test_1():
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent", type=int)
    p1 = parser.parse_args(["--parent=100"])
    p2 = parser.parse_args(["--parent", "100"])
    print(p1)
    print(p2)
