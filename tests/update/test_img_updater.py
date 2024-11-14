from pathlib import Path
import shutil

from wemo.base.logger import default_console_logger
from wemo.update.img_updater import ImageUpdater
from wemo.model.dto import MomentMsg
from wemo.base.constant import PROJECT_DIR, DATA_DIR

wxid = "test_update"
user_img_dir = Path(DATA_DIR.joinpath(wxid), "data", "image")
cache_img_dir = Path(DATA_DIR.joinpath(wxid), "cache", "image")
LOG = default_console_logger(wxid)


def setup_module():
    shutil.rmtree(user_img_dir, ignore_errors=True)
    user_img_dir.mkdir(parents=True, exist_ok=True)


def test_handle_moment(mocker):
    img_size = 1951
    thm_size = 1951
    mock_value_img = b"\xff\xd8" + b"1" * (img_size - 2)
    mock_value_thm = b"\xff\xd8" + b"0" * (thm_size - 2)
    mocker.patch(
        "wemo.update.img_updater.get_image_from_wx_server",
        side_effect=[mock_value_img, mock_value_thm] * 10,
    )
    file_path = PROJECT_DIR.joinpath("tests", "static", f"{wxid}.xml")
    with open(file_path, "r", encoding="utf-8") as f:
        xml = f.read()
    moment = MomentMsg.parse_xml(xml)
    exp = ImageUpdater(
        user_data_img_dir=user_img_dir, user_cache_img_dir=cache_img_dir, logger=LOG
    )
    exp.update_by_moment(moment)
