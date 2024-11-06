import hashlib
import os
import shutil
import subprocess
import traceback
from datetime import date
from config.constant import BIN_DIR
from config.user_init import APP_USER_SNS_DIR, WX_SNS_CACHE_DIR
import filetype
from config.logger import LOG
from utils.helper import get_all_month_between_dates


def get_output_path(md5, duration):
    return APP_USER_SNS_DIR.joinpath("videos", f"{md5}_{duration}.mp4")


def calculate_md5(file_path):
    with open(file_path, "rb") as f:
        file_content = f.read()
    return hashlib.md5(file_content).hexdigest()


def get_ffprobe_path():
    return BIN_DIR.joinpath("ffprobe.exe")


def get_ffmpeg_path():
    return BIN_DIR.joinpath("ffmpeg.exe")


class VideoDecrypter:

    def __init__(self):
        self.sns_cache_path = WX_SNS_CACHE_DIR
        self.sns_video_path = APP_USER_SNS_DIR.joinpath("videos")
        self.sns_video_path.mkdir(exist_ok=True)

    def get_video_duration(self, video_path) -> float:
        """获取视频时长"""
        ffprobe_path = get_ffprobe_path()
        if not os.path.exists(ffprobe_path):
            LOG.error("Wrong ffprobe path:" + ffprobe_path)
            return 0
        ffprobe_cmd = f'"{ffprobe_path}"  -i "{video_path}" -show_entries format=duration -v quiet -of csv="p=0"'
        p = subprocess.Popen(
            ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        print(ffprobe_cmd)
        out, err = p.communicate()
        if len(str(err, "gbk")) > 0:
            print(f"subprocess 执行结果：out:{out} err:{str(err, 'gbk')}")
            return 0
        if len(str(out, "gbk")) == 0:
            return 0
        return float(out)

    def decrypt_videos(self, start: date, end: date) -> None:
        """将视频文件从缓存中复制出来，重命名为{md5}_{duration}.mp4
        duration单位为秒
        """
        year_month_list = get_all_month_between_dates(start, end)

        total_files = 0
        processed_files = 0
        for year_month in year_month_list:
            source_dir = self.sns_cache_path.joinpath(year_month)
            total_files = total_files + len(list(source_dir.rglob("*")))

        for year_month in year_month_list:
            source_dir = self.sns_cache_path.joinpath(year_month)
            for file in source_dir.rglob("*"):
                try:
                    file_type = filetype.guess(file.resolve())
                    if file_type and file_type.extension == "mp4":
                        print("Process Video: " + str(file.resolve()))
                        md5 = calculate_md5(file.resolve())
                        print("video md5: " + md5)
                        duration = self.get_video_duration(str(file.resolve()))
                        print("video duration: " + str(duration))
                        shutil.copy(
                            file.resolve(),
                            self.sns_video_path.joinpath(f"{md5}_{duration}.mp4"),
                        )
                except Exception:
                    traceback.print_exc()
                processed_files = processed_files + 1
