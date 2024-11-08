import re


def test_1():

    s = """<contentDesc>年前最‮123‬波内调活‮动‮123‬‮123‬</contentDesc>"""
    pattern = re.compile(r"\u202e(.*?)\u202c")
    res = pattern.findall(s)
    for item in res:
        print(item)
