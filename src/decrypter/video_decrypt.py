import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import traceback
from datetime import date
from common import SC, RC, LOG
import filetype
from utils import get_months_between_dates


def calculate_md5(file_path):
    with open(file_path, "rb") as f:
        file_content = f.read()
    return hashlib.md5(file_content).hexdigest()


def get_ffprobe_path():
    return SC.BIN_DIR.joinpath("ffprobe.exe")


def get_ffmpeg_path():
    return SC.BIN_DIR.joinpath("ffmpeg.exe")


def get_video_duration(video_path: Path) -> float:
    """获取视频时长"""
    ffprobe_path = get_ffprobe_path()
    if not ffprobe_path.exists():
        LOG.error("Wrong ffprobe path:" + ffprobe_path)
        return 0
    ffprobe_cmd = f'"{ffprobe_path}"  -i "{video_path}" -show_entries format=duration -v quiet -of csv="p=0"'
    p = subprocess.Popen(
        ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    LOG.debug(f"ffprobe cmd: {ffprobe_cmd}")
    out, err = p.communicate()
    if len(str(err, "gbk")) > 0:
        LOG.info(f"subprocess 执行结果: out:{out} err:{str(err, 'gbk')}")
        return 0
    if len(str(out, "gbk")) == 0:
        return 0
    return float(out)


class VideoDecrypter:

    def __init__(self):
        self.wx_sns_cache = RC.WX_SNS_CACHE_DIR
        self.sns_cache_video = RC.USER_CACHE_SNS_VIDEO

    def decrypt_videos(self, start: date, end: date) -> None:
        """将视频文件从缓存中复制出来，重命名为{md5}_{duration}.mp4
        duration单位为秒
        """
        year_month_list = get_months_between_dates(start, end)

        for year_month in year_month_list:
            source_dir = self.sns_cache_video.joinpath(year_month)
            os.makedirs(self.sns_cache_video.joinpath(year_month), exist_ok=True)

        for year_month in year_month_list:
            source_dir = self.wx_sns_cache.joinpath(year_month)
            for file in source_dir.rglob("*"):
                try:
                    file_type = filetype.guess(file.resolve())
                    if file_type and file_type.extension == "mp4":
                        md5 = calculate_md5(file.resolve())
                        duration = get_video_duration(str(file.resolve()))
                        output_path = self.sns_cache_video.joinpath(
                            year_month, f"{md5}_{duration}.mp4"
                        )
                        LOG.info(f"处理 Video: {output_path.name}")
                        shutil.copy(file.resolve(), output_path)
                except Exception:
                    traceback.print_exc()
