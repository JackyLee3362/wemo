from pathlib import Path
import shutil

import pytest
from wemo import constant
from wemo.database.micro_msg import MicroMsgCache, Contact
from wemo.database.misc import ContactHeadImg1, MiscCache
from wemo.database.sns import FeedsV20, SnsCache
from wemo.decrypter import DBDecrypter, ImageDecrypter, VideoDecrypter
from wemo.user import User

user_dir = constant.DATA_DIR.joinpath(__name__)
user = User.mock_user(__name__)


def setup_module():
    shutil.rmtree(user_dir, ignore_errors=True)
    user.init_user_dir()
    pass


def teardown_module():
    print("bye, test_decrypter")


def test_db_decrypter():
    d = DBDecrypter(
        wx_key=None,
        src_dir=user.wx_dir,
        dst_dir=user.cache_dir.db_dir,
        db_name_list=user.db_name_list,
        logger=user.logger,
    )
    d.decrypt()


def test_cache():
    db_dir = user.cache_dir.db_dir
    c1 = MicroMsgCache(user_cache_db_dir=db_dir, logger=user.logger)
    c1.init_db()
    c1.count_all(Contact)
    c2 = MiscCache(user_cache_db_dir=db_dir, logger=user.logger)
    c2.init_db()
    c2.count_all(ContactHeadImg1)
    c3 = SnsCache(user_cache_db_dir=db_dir, logger=user.logger)
    c3.init_db()
    c3.count_all(FeedsV20)


def test_image_decrypter():
    d = ImageDecrypter(
        src_dir=user.wx_dir, dst_dir=user.cache_dir.img_dir, logger=user.logger
    )
    d.decrypt()


def test_video_decrypter():
    d = VideoDecrypter(
        src_dir=user.wx_dir,
        dst_dir=user.cache_dir.video_dir,
        bin_path=constant.BIN_DIR,
        logger=user.logger,
    )
    d.decrypt()
