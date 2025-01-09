import shutil

from wemo.backend.sync.sync_service import SyncService
from wemo.backend.utils.mock import mock_ctx

wxid = "test_sync"
ctx = mock_ctx(wxid)


def setup_module():
    shutil.rmtree(ctx.user_data_dir)


def test_cache_updater():
    syncer = SyncService(ctx)
    syncer.init()

    syncer.sync_db()
    syncer.sync_img()
    syncer.sync_video()
