import shutil
from wemo.backend.utils.mock import mock_ctx
from wemo.backend.sync.sync_service import SyncService

wxid = "test_sync"
ctx = mock_ctx(wxid)


def setup_module():
    shutil.rmtree(ctx.user_data_dir)
    ctx.init_user_info()


def test_cache_updater():
    syncer = SyncService(ctx)
    syncer.init()

    syncer.sync_db()
    syncer.sync_img()
    syncer.sync_video()
