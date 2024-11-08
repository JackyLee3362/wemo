import hashlib
from logging import Logger, getLogger
from pathlib import Path
import shutil
import subprocess
from datetime import date
import filetype

from .decrypter import Decrypter


class VideoDecrypter(Decrypter):

    def __init__(self, src_dir: Path, dst_dir: Path, bin_path: Path, logger: Logger):
        super.__init__(src_dir=src_dir, dst_dir=dst_dir, logger=logger)
        self.bin_path = bin_path
        self.src_dir = src_dir
        self.dst_dir = dst_dir
        self.logger = logger or getLogger(__name__)

    @property
    def ffprobe_path(self):
        return self.bin_path.joinpath("ffprobe.exe")

    @property
    def ffmpeg_path(self):
        return self.bin_path.joinpath("ffmpeg.exe")

    def decrypt_videos(self, start: date, end: date) -> None:
        """
        将视频文件从缓存中复制出来，重命名为 [md5_duration.mp4]
        """
        y_m_list = self.get_months_between_dates(start, end)

        for y_m in y_m_list:
            src_dir = self.dst_dir.joinpath(y_m)
            src_dir.joinpath(y_m).mkdir(exist_ok=True)
            for file in src_dir.rglob("*"):
                file_type = filetype.guess(file)
                if file_type and file_type.extension == "mp4":
                    self.logger.info(f"[ HANDLE VIDEO ]: {file}")
                    md5 = self.calculate_md5(file)
                    duration = self.get_video_duration(file)
                    video_dst_path = self.src_dir.joinpath(f"{md5}_{duration}.mp4")
                    shutil.copy(file.resolve(), video_dst_path)

    def calculate_md5(self, file: Path):
        with open(file, "rb") as f:
            content = f.read()
        return hashlib.md5(content).hexdigest()

    def get_video_duration(self, video_path: Path) -> float:
        """获取视频时长"""
        ffprobe_path = self.ffprobe_path
        if not ffprobe_path.exists():
            self.logger.error(f"[ NOT EXIST ]: {ffprobe_path}")
            return 0
        ffprobe_cmd = f'"{ffprobe_path}"  -i "{video_path}" -show_entries format=duration -v quiet -of csv="p=0"'
        p = subprocess.Popen(
            ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        self.logger.debug(f"ffprobe cmd: {ffprobe_cmd}")
        out, err = p.communicate()
        if len(str(err, "gbk")) > 0:
            self.logger.info(f"subprocess 执行结果: out:{out} err:{str(err, 'gbk')}")
            return 0
        if len(str(out, "gbk")) == 0:
            return 0
        return float(out)
