import shutil
from wemo.backend.sync.sync_service import SyncService
from wemo.backend.ctx import Context

wxid = "test_sync"
ctx = Context.mock_ctx(wxid)


def setup_module():
    shutil.rmtree(ctx.user_data_dir)
    ctx.init_user_info()


def test_cache_updater():
    syncer = SyncService(ctx)
    syncer.init()

    syncer.sync_db()
    syncer.sync_img()
    syncer.sync_video()
