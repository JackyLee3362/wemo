import shutil
from wemo.sync.sync_service import SyncService
from wemo.model.ctx import Context

wxid = "test_sync"
user = Context.mock_ctx(wxid)


def setup_module():
    shutil.rmtree(user.user_data_dir)
    user.init()


def test_cache_updater():
    syncer = SyncService(user)
    syncer.init()

    syncer.sync_db()
    syncer.sync_img()
    syncer.sync_video()
