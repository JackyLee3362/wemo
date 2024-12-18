from pathlib import Path
import pytest
import json

from wemo.backend.base.scaffold import Scaffold
from wemo.backend.backend import BackendImpl

TEST_KEY = "foo"
SECRET_KEY = "config"


def common_object_test(app: Scaffold):
    assert app.secret_key == "config"
    assert app.config["TEST_KEY"] == "foo"
    assert "TestConfig" not in app.config


def test_config_from_pyfile():
    app = BackendImpl(__name__)
    app.config.from_pyfile(__file__)
    common_object_test(app)


def test_config_from_object():
    app = BackendImpl(__name__)
    app.config.from_object(__name__)
    common_object_test(app)


def test_config_from_file_json():
    app = BackendImpl(__name__)
    current_dir = Path(__file__).parent.parent
    app.config.from_file(current_dir.joinpath("static", "config.json"), json.load)
    common_object_test(app)


def test_config_from_file_toml():
    tomllib = pytest.importorskip("tomllib", reason="tomllib added in 3.11")
    app = BackendImpl(__name__)
    current_dir = Path(__file__).parent.parent
    app.config.from_file(
        current_dir.joinpath("static", "config.toml"), tomllib.load, text=False
    )
    common_object_test(app)
