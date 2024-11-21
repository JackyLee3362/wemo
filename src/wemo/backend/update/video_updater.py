import logging
import shutil
from pathlib import Path
from typing import override

from wemo.backend.model.moment import MomentMsg
from wemo.backend.update.updater import Updater
from wemo.backend.utils.utils import singleton, find_video_by_md5_or_duration


@singleton
class VideoUpdater(Updater):
    def __init__(self, src_dir: Path, dst_dir: Path, logger: logging.Logger = None):
        super().__init__(src_dir=src_dir, dst_dir=dst_dir, logger=logger)

    @override
    def update_by_moment(self, moment: MomentMsg) -> list[str]:
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
            self.handle_video(src_path, dst_path, video.url.md5, video.videoDuration)

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
            self.logger.warning(
                f"[ VIDEO UPDATER ] Video({v_name}) not found in cache!"
            )
        else:
            shutil.copy(video_cached_path, video_path)
