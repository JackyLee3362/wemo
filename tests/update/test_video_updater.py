from pathlib import Path
import shutil

from wemo.base.logger import default_console_logger
from wemo.update.video_updater import VideoUpdater
from wemo.model.dto import MomentMsg
from wemo.base.constant import PROJECT_DIR, DATA_DIR

wxid = "test_update"
user_data_video_dir = Path(DATA_DIR.joinpath(wxid), "data", "video")
user_cache_video_dir = Path(DATA_DIR.joinpath(wxid), "cache", "video")
LOG = default_console_logger(wxid)


def setup_module():
    shutil.rmtree(user_data_video_dir, ignore_errors=True)
    user_data_video_dir.mkdir(parents=True, exist_ok=True)


def test_handle_moment():
    file_path = PROJECT_DIR.joinpath("tests", "static", f"{wxid}.xml")
    with open(file_path, "r", encoding="utf-8") as f:
        xml = f.read()
    moment = MomentMsg.parse_xml(xml)
    exp = VideoUpdater(
        user_data_video_dir=user_data_video_dir,
        user_cache_video_dir=user_cache_video_dir,
        logger=LOG,
    )
    exp.update_by_moment(moment)