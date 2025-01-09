from wemo.backend.common import constant
from wemo.backend.database.micro_msg import MicroMsgCache, Contact
from wemo.backend.database.misc import ContactHeadImg1, MiscCache
from wemo.backend.database.sns import Feed, SnsCache
from wemo.backend.utils.mock import mock_ctx
from wemo.backend.sync.video_syncer import VideoSync
from wemo.backend.sync.db_syncer import DBSyncer
from wemo.backend.sync.img_syncer import ImgSyncer

wxid = "test_sync"
user = mock_ctx(wxid)


def setup_module():
    # shutil.rmtree(user.user_dir, ignore_errors=True)
    user.init_user_info()


def teardown_module():
    print("bye, test_decrypter")


def test_db_decrypter():
    db_dir = user.user_cache_dir.db_dir
    c1 = MiscCache(user_cache_db_url=db_dir.joinpath("Misc.db"))
    c1.init()
    c1.count_all(c1.table_cls_list[0])
    d = DBSyncer(
        wx_key=None,
        src_dir=user.wx_dir,
        dst_dir=user.user_cache_dir.db_dir,
        db_name_list=user.db_name_list,
    )
    d.sync()


def test_cache():
    db_dir = user.user_cache_dir.db_dir
    c1 = MicroMsgCache(user_cache_db_url=db_dir.joinpath("MicroMsg.db"))
    c1.init()
    c1.count_all(Contact)
    c2 = MiscCache(user_cache_db_url=db_dir.joinpath("Misc.db"))
    c2.init()
    c2.count_all(ContactHeadImg1)
    c3 = SnsCache(user_cache_db_url=db_dir.joinpath("Sns.db"))
    c3.init()
    c3.count_all(Feed)


def test_image_decrypter():
    d = ImgSyncer(src_dir=user.wx_dir, dst_dir=user.user_cache_dir.img_dir)
    d.sync()


def test_video_decrypter():
    d = VideoSync(
        src_dir=user.wx_dir,
        dst_dir=user.user_cache_dir.video_dir,
        bin_path=constant.BIN_DIR,
    )
    d.sync()
