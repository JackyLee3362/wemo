import math
import os
import re
from pathlib import Path
import shutil
from typing import Optional
from common.logger import LOG
from common.user_constant import RC
from model.moment_msg import MomentMsg
from utils.wrapper import singleton


@singleton
class VideoExporter:
    def __init__(self):
        self.app_videos = RC.USER_SNS_VIDEO
        self.app_cache_videos = RC.USER_CACHE_SNS_VIDEO

    def _find_video_by_md5(self, path: Path, md5: str) -> Optional[Path]:
        """
        使用MD5匹配视频
        """
        pattern = re.compile(r"^(.*?)(?=_)")

        for file_path in path.iterdir():
            match = pattern.search(file_path.name)
            if match:
                filename_md5 = match.group()
                if filename_md5 == md5:
                    return file_path

    def _find_video_by_duration(self, path: Path, duration: float) -> Optional[Path]:
        """
        使用视频时长匹配视频
        """
        pattern = re.compile(r"_([0-9.]+)\.mp4")

        for file_path in path.iterdir():
            match = pattern.search(file_path.name)
            if match:
                filename_duration = float(match.group(1))
                if math.isclose(filename_duration, duration, abs_tol=0.005):
                    return file_path

    def handle_videos_from_moment(self, msg: MomentMsg) -> list[str]:
        """获取一条朋友圈的全部视频， 返回值是一个文件路径列表"""
        mediaList = msg.timelineObject.ContentObject.mediaList
        year_month = msg.create_year_month
        dir_path = self.app_cache_videos.joinpath(year_month)
        os.makedirs(dir_path, exist_ok=True)
        if not mediaList:
            return None

        for media_item in mediaList.media:
            if media_item.type == "6":
                md5 = media_item.url.md5
                duration = media_item.videoDuration
                video_name = f"{msg.create_date}_{md5}.mp4"
                video_path = self.app_videos.joinpath(video_name)
                if video_path.exists():
                    return video_path
                rounded_duration = round(float(duration), 2)
                # 先用MD5匹配缓存中的视频
                video_cached_path = self._find_video_by_md5(dir_path, md5)
                # 如果找不到使用视频时长再次匹配
                if not video_cached_path:
                    video_cached_path = self._find_video_by_duration(
                        dir_path, rounded_duration
                    )
                if video_cached_path:
                    shutil.copy(video_cached_path, video_path)
                    return video_path
                # 如果还是找不到，就从微信服务器下载(todo)
                LOG.error(f"{msg.user_name} 找不到该用户的视频")
