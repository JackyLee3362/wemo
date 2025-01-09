from pathlib import Path
from wemo.backend.utils.mock import mock_ctx

mock_wx_id = Path(__file__).stem


def test_mock_ctx():
    ctx = mock_ctx(mock_wx_id)
    ctx.init_user_info()
    assert ctx.wx_id == mock_wx_id
    assert ctx.wx_key is None


def test_ctx_property():
    ctx = mock_ctx(mock_wx_id)
    ctx.init_user_info()
    print(ctx.root_dir)
    print(ctx.user_data_dir)
