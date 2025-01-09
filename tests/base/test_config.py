from wemo.backend.base.config import TomlConfig
from wemo.backend.common import constant


def test_read_config():
    file = constant.CONFIG_DEFAULT_FILE
    config = TomlConfig()
    config.load_file(file)
    assert config.app.name == "wemo"
