from config.config import config


def test_config():
    assert isinstance(config.get("app"), dict)
