from wemo.backend.base.scaffold import Scaffold

TEST_KEY = "foo"
SECRET_KEY = "config"


def common_object_test(app: Scaffold):
    assert app.config["TEST_KEY"] == "foo"
    assert "TestConfig" not in app.config
