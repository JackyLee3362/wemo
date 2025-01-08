from pathlib import Path
import shutil
import logging

from wemo.backend.update.video_updater import VideoUpdater
from wemo.backend.model.moment import MomentMsg
from wemo.backend.base.constant import PROJECT_DIR, DATA_DIR

wxid = "test_update"
user_data_video_dir = Path(DATA_DIR.joinpath(wxid), "data", "video")
user_cache_video_dir = Path(DATA_DIR.joinpath(wxid), "cache", "video")
logger = logging.getLogger(__name__)


def setup_module():
    shutil.rmtree(user_data_video_dir, ignore_errors=True)
    user_data_video_dir.mkdir(parents=True, exist_ok=True)


def test_handle_moment():
    file_path = PROJECT_DIR.joinpath("tests", "static", f"{wxid}.xml")
    with open(file_path, "r", encoding="utf-8") as f:
        xml = f.read()
    moment = MomentMsg.parse_xml(xml)
    exp = VideoUpdater(
        dst_dir=user_data_video_dir,
        src_dir=user_cache_video_dir,
    )
    exp.update_by_moment(moment)
