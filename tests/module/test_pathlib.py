from pathlib import Path

def test_1():
    p = Path(r"C:\Users\JACKYLEE\Documents\WeChat Files\wxid_h8cex1v6segm21")
    print(p.exists())

    for path in p.glob("**/*.db"):
        print(path.stem, path)