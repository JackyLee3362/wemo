from wemo.backend.backend import BackendImpl
from wemo.backend.base import constant


def test_config_of_constant():
    app = BackendImpl(__name__)

    app.config.from_object(constant)
    print(app.config["BIN_DIR"])
    assert app.config["BIN_DIR"] is not None
