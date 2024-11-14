import hashlib
import shutil
import subprocess
from datetime import date, datetime
from logging import Logger
from pathlib import Path
from typing import override

import filetype

from wemo.sync.sync import Syncer
from wemo.utils.utils import get_months_between_dates


class VideoSync(Syncer):

    def __init__(
        self, src_dir: Path, dst_dir: Path, bin_path: Path, logger: Logger = None
    ):
        super().__init__(src_dir=src_dir, dst_dir=dst_dir, logger=logger)
        self.bin_path = bin_path

    @override
    def sync(self, begin: datetime, end: datetime):
        self._sync_video_list(begin, end)

    @property
    def ffprobe_path(self):
        return self.bin_path.joinpath("ffprobe.exe")

    @property
    def ffmpeg_path(self):
        return self.bin_path.joinpath("ffmpeg.exe")

    def _sync_video_list(self, begin: date = None, end: date = None) -> None:
        """
        将视频文件从缓存中复制出来，重命名为 ./year_month/{md5}_{duration}.mp4
        """
        if begin is None and end is None:
            y_m_list = self.get_months_by_existing_dir()
        else:
            y_m_list = get_months_between_dates(begin, end)

        for y_m in y_m_list:
            src_dir = self.src_dir.joinpath(y_m)
            dst_dir = self.dst_dir.joinpath(y_m)
            dst_dir.mkdir(parents=True, exist_ok=True)
            for file in src_dir.rglob("*"):
                file_type = filetype.guess(file)
                if file_type and file_type.extension == "mp4":
                    self._handle_video(file, dst_dir)

    def _handle_video(self, file: Path, dst_dir: Path):
        self.logger.debug(f"[ VIDEO DECRYPTER ] File({file.name}) decrypting...")
        md5 = self._calculate_md5(file)
        dur = self._get_video_duration(file)
        video_dst_path = dst_dir.joinpath(f"{md5}_{dur}.mp4")
        if not video_dst_path.exists():
            self.logger.debug(f"[ VIDEO DECRYPTER ] copy file from Path({file.name})")
            shutil.copy(file, video_dst_path)

        pass

    def _calculate_md5(self, file: Path):
        with open(file, "rb") as f:
            content = f.read()
        return hashlib.md5(content).hexdigest()

    def _get_video_duration(self, video_path: Path) -> float:
        """获取视频时长"""
        ffprobe_path = self.ffprobe_path
        if not ffprobe_path.exists():
            self.logger.warning(
                f"[ VIDEO DECRYPTER ] ffprobe Path({ffprobe_path}) is not exist."
            )
            return 0
        ffprobe_cmd = f'"{ffprobe_path}"  -i "{video_path}" -show_entries format=duration -v quiet -of csv="p=0"'
        p = subprocess.Popen(
            ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        # self.logger.debug(f"ffprobe cmd: {ffprobe_cmd}")
        out, err = p.communicate()
        if len(str(err, "gbk")) > 0:
            self.logger.warning(
                f"[ VIDEO DECRYPTER ] out({out}) and err({str(err, 'gbk')})"
            )
            return 0
        if len(str(out, "gbk")) == 0:
            return 0
        return float(out)
