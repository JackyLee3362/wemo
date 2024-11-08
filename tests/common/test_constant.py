import common


def test_init_common():
    common.SC
    common.RC

def test_config_env():
    common.config.get("app.env")