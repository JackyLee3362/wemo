import shutil

from wemo.backend.database.db_service import DBService
from wemo.backend.update.updater_service import UserDataUpdateService
from wemo.backend.utils.mock import mock_ctx

wxid = "test_update"
ctx = mock_ctx(wxid)


def setup_module():
    shutil.rmtree(ctx.user_data_dir)


def test_user_data_updater():
    db = DBService(ctx)
    db.init()
    user_data_updater = UserDataUpdateService(ctx, db)
    user_data_updater.init()
    user_data_updater.update_db()
