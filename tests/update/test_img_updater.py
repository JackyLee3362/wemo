from pathlib import Path
import shutil

from wemo.backend.base.logger import create_app_logger
from wemo.backend.update.img_updater import ImageUpdater
from wemo.backend.model.moment import MomentMsg
from wemo.backend.base.constant import PROJECT_DIR, DATA_DIR

wxid = "test_update"
user_img_dir = Path(DATA_DIR.joinpath(wxid), "data", "image")
cache_img_dir = Path(DATA_DIR.joinpath(wxid), "cache", "image")
logger = create_app_logger(wxid)


def setup_module():
    shutil.rmtree(user_img_dir, ignore_errors=True)
    user_img_dir.mkdir(parents=True, exist_ok=True)


def test_handle_moment(mocker):
    img_size = 1951
    thm_size = 1951
    mock_value_img = b"1" * img_size
    mock_value_thm = b"0" * thm_size
    mocker.patch(
        "wemo.utils.helper.get_img_from_server",
        side_effect=[mock_value_img, mock_value_thm] * 10,
    )
    file_path = PROJECT_DIR.joinpath("tests", "static", f"{wxid}.xml")
    with open(file_path, "r", encoding="utf-8") as f:
        xml = f.read()
    moment = MomentMsg.parse_xml(xml)
    exp = ImageUpdater(dst_dir=user_img_dir, src_dir=cache_img_dir, logger=logger)
    exp.update_by_moment(moment)


def test_handle_moment_private(mocker):
    img_size = 1951
    thm_size = 1951
    mock_value_img = b"1" * img_size
    mock_value_thm = b"0" * thm_size
    mocker.patch(
        "wemo.utils.helper.get_img_from_server",
        side_effect=[mock_value_img, mock_value_thm] * 10,
    )
    file_path = PROJECT_DIR.joinpath("tests", "static", f"{wxid}_private.xml")
    with open(file_path, "r", encoding="utf-8") as f:
        xml = f.read()
    moment = MomentMsg.parse_xml(xml)
    exp = ImageUpdater(dst_dir=user_img_dir, src_dir=cache_img_dir, logger=logger)
    exp.update_by_moment(moment)
