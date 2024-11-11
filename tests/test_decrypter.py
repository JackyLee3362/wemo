from pathlib import Path
import shutil

import pytest
from wemo.decrypter import DBDecrypter, ImageDecrypter, VideoDecrypter
from wemo.user import User

cur_file_name = Path(__file__).stem
user = User.mock_user(cur_file_name)
shutil.rmtree(user.cache_dir)
user.init_dir()


@pytest.fixture(autouse=True)
def run_around_test():
    yield
    # shutil.rmtree(user.user_dir)


def test_db_decrypter():
    d = DBDecrypter(
        wx_key=user.wx_key,
        src_dir=user.wx_dir,
        dst_dir=user.cache_db_dir,
        db_name_list=["Sns", "Misc", "MicroMsg"],
    )
    d.decrypt()


def test_image_decrypter():
    d = ImageDecrypter(src_dir=user.wx_sns_cache_dir, dst_dir=user.cache_sns_image_dir)
    d.decrypt()


def test_video_decrypter():
    bin_dir = user.config.get("BIN_DIR")
    d = VideoDecrypter(
        src_dir=user.wx_sns_cache_dir,
        dst_dir=user.cache_sns_video_dir,
        bin_path=bin_dir,
    )
    d.decrypt()
