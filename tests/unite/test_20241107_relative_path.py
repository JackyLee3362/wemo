from pathlib import Path

from common.constant import SC


def test_1():
    f1 = Path(__file__)
    f2 = Path(SC.PROJECT_DIR)  # 其他不太行
    res = None
    if f1.exists() and f2.exists():
        res = f1.relative_to(f2)

    print(type(res))
    print(res)
