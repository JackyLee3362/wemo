import shutil

from wemo.service.updater_service import UserDataUpdateService
from wemo.model.user import User

user = User.mock_user(__name__)


def setup_module():
    shutil.rmtree(user.data_dir)
    user.init_user_dir()


def test_user_data_updater():
    user_data_updater = UserDataUpdateService(user)
    user_data_updater.update_db()
