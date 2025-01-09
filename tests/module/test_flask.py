import flask

app = flask.Flask(__name__)
app.config["TESTING"] = True


def test_1():
    print(app.root_path)
