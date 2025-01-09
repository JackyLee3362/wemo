from pathlib import Path

from wemo.backend.utils.mock import mock_ctx

mock_wx_id = Path(__file__).stem


def test_mock_ctx():
    ctx = mock_ctx(mock_wx_id)
    assert ctx.wx_id == mock_wx_id
    assert ctx.wx_key is None


def test_ctx_property():
    ctx = mock_ctx(mock_wx_id)
    print(ctx.root_path)
    print(ctx.user_data_dir)
