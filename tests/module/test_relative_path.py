from pathlib import Path

def test_1():
    f1 = Path(__file__)
    f2 = f1.parent.parent  # 其他不太行
    res = None
    if f1.exists() and f2.exists():
        res = f1.relative_to(f2)

    print(type(res))
    print(res)
