from jinja2 import Template


def test_1():
    name = ["a", "b", "c"]
    t = Template("Hello {{ name|length }}!")
    print(t.render(name=name))
