import re


def test_1():

    s = """<contentDesc>年前最‮123‬波内调活‮动‮123‬‮123‬</contentDesc>"""
    pattern = re.compile(r"\u202e(.*?)\u202c")
    res = pattern.findall(s)
    for item in res:
        print(item)


def test_2():
    s = "2024-0111"
    pattern = re.compile("^20\d{2}-[01][0-9]$")
    res = pattern.match(s)
    print(res)
