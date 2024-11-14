from wemo.app import Wemo
from wemo.base import constant


def test_config_of_constant():
    app = Wemo(__name__)

    app.config.from_object(constant)
    print(app.config["BIN_DIR"])
    assert app.config["BIN_DIR"] is not None
