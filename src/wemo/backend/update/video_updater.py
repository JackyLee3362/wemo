import logging
import shutil
from pathlib import Path

from wemo.backend.common.model import MomentMsg
from wemo.backend.update.updater import Updater
from wemo.backend.utils.utils import singleton, find_video_by_md5_or_duration


logger = logging.getLogger(__name__)


@singleton
class VideoUpdater(Updater):
    def __init__(self, src_dir: Path, dst_dir: Path):
        super().__init__(src_dir=src_dir, dst_dir=dst_dir)

    def update_by_moment(self, moment: MomentMsg, suffix: str = "") -> list[str]:
        """获取一条朋友圈的全部视频， 返回值是一个文件路径列表"""
        media_list = moment.medias
        year_month = moment.year_month
        src_path = self.src_dir.joinpath(year_month)
        dst_path = self.dst_dir.joinpath(year_month)
        src_path.mkdir(parents=True, exist_ok=True)
        dst_path.mkdir(parents=True, exist_ok=True)
        if not media_list:
            return []
        for video in moment.videos:
            try:
                self.handle_video(
                    src_path, dst_path, video.url.md5, video.videoDuration
                )
            except FileNotFoundError as e:
                msg = e.args[0] if len(e.args) > 0 else ""
                logger.warning(
                    f"[ VIDEO UPDATER ] {moment.time} {suffix}-{msg}\n{moment.desc_brief}"
                )

    def handle_video(self, src_path: Path, dst_path: Path, md5: str, duration: str):
        v_name = f"{md5}_{duration}.mp4"
        video_path = dst_path.joinpath(v_name)
        if video_path.exists():
            return video_path
        # 使用 md5 和视频匹配
        video_cached_path = find_video_by_md5_or_duration(
            src_path, md5, float(duration)
        )
        if not video_cached_path:
            raise FileNotFoundError(f"Video({v_name}) not found in cache!")
        else:
            shutil.copy(video_cached_path, video_path)
