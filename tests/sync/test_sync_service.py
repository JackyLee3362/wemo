import shutil
from wemo.sync.sync_service import SyncService
from wemo.model.ctx import Context

wxid = "test_sync"
ctx = Context.mock_ctx(wxid)


def setup_module():
    shutil.rmtree(ctx.user_data_dir)
    ctx.init()


def test_cache_updater():
    syncer = SyncService(ctx)
    syncer.init()

    syncer.sync_db()
    syncer.sync_img()
    syncer.sync_video()