from pathlib import Path
from wemo.user import User

mock_wx_id = Path(__file__).stem


def test_mock_user():
    user = User.mock_user(mock_wx_id)
    user.init_user_dir()
    assert user.wx_id == mock_wx_id
    assert user.wx_key is None


def a(): ...
