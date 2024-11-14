import shutil
from wemo.service.sync_service import CacheSyncService
from wemo.model.user import User

user = User.mock_user(__name__)


def setup_module():
    shutil.rmtree(user.data_dir)
    user.init_user_dir()


def test_cache_updater():
    cache_updater = CacheSyncService(user)
    cache_updater.sync_db()
    cache_updater.sync_img()
    cache_updater.sync_video()


