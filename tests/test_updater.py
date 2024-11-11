from pathlib import Path
import shutil
from wemo.base.logging import default_console_logger
from wemo.updater import CacheUpdater, UserDataUpdater
from wemo.database import MicroMsg, MicroMsgCache, Misc, MiscCache, Sns, SnsCache
from wemo.user import User

user = User.mock_user(__name__)


def setup_module():
    shutil.rmtree(user.data_dir)
    user.init_user_dir()


def test_cache_updater():
    cache_updater = CacheUpdater(user)
    cache_updater.update_db()
    cache_updater.update_img()
    cache_updater.update_video()


def test_user_data_updater():
    # UserDataUpdater(user)
    pass
