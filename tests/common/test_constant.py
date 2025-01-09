from pathlib import Path
from wemo.backend.common import constant


def test_common():
    print(constant.CONFIG_DEFAULT_FILE)
    assert constant.CONFIG_DEFAULT_FILE == Path(constant.CONFIG_DIR) / "app.toml"
