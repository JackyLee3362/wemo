from pathlib import Path
from wemo.backend.ctx import Context

mock_wx_id = Path(__file__).stem


def test_mock_ctx():
    ctx = Context.mock_ctx(mock_wx_id)
    ctx.init()
    assert ctx.wx_id == mock_wx_id
    assert ctx.wx_key is None


def test_ctx_property():
    ctx = Context.mock_ctx(mock_wx_id)
    ctx.init()
    print(ctx.root_dir)
    print(ctx.user_data_dir)
