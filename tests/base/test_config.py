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
