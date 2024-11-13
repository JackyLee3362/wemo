import logging
import shutil
from pathlib import Path

from wemo.model.dto import MomentMsg
from wemo.utils.utils import singleton, find_video_by_md5_or_duration


@singleton
class VideoUpdater:
    def __init__(
        self,
        user_data_video_dir: Path,
        user_cache_video_dir: Path,
        logger: logging.Logger = None,
    ):
        self.data_video_dir = user_data_video_dir
        self.cache_video_dir = user_cache_video_dir
        self.logger = logger

    def handle_moment(self, msg: MomentMsg) -> list[str]:
        """获取一条朋友圈的全部视频， 返回值是一个文件路径列表"""
        media_list = msg.medias
        year_month = msg.year_month
        src_path = self.cache_video_dir.joinpath(year_month)
        dst_path = self.data_video_dir.joinpath(year_month)
        dst_path.mkdir(parents=True, exist_ok=True)
        if not media_list:
            return []
        for video in msg.videos:
            self.handle_video(src_path, dst_path, video.url.md5,
                              video.videoDuration)

    def handle_video(self, src_path: Path, dst_path: Path, md5: str,
        duration: str):
        video_name = f"{md5}_{duration}.mp4"
        video_path = dst_path.joinpath(video_name)
        if video_path.exists():
            return video_path
        # 使用 md5 和视频匹配
        video_cached_path = find_video_by_md5_or_duration(src_path, md5,
                                                          float(duration))
        if video_cached_path:
            shutil.copy(video_cached_path, video_path)
            return video_path
        self.logger.error(
            f"[ NOT FIND ] Video({video_name}) not found in cache!")
