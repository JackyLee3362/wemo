from datetime import date
from logging import Logger, getLogger
from pathlib import Path
from collections import namedtuple
import re
from typing import override

from wemo.utils import get_months_between_dates

from .helper import decrypt
import hashlib
import shutil
import subprocess
import filetype


class Decrypter:
    def __init__(
        self,
        src_dir: Path = None,
        dst_dir: Path = None,
        logger: Logger = None,
    ):
        self.src_dir = src_dir
        self.dst_dir = dst_dir
        self.logger = logger or getLogger(__name__)

    def decrypt(self, *args, **kwargs):
        raise NotImplementedError("Not Implemented")

    def get_months_by_existing_dir(self):
        res = []
        pattern = re.compile(r"^20\d{2}-[01][0-9]$")
        for file in self.src_dir.iterdir():
            if file.is_dir() and pattern.match(file.name) is not None:
                res.append(file.name)
        return res


class DBDecrypter(Decrypter):
    """
    数据库解密器
    """

    def __init__(
        self,
        wx_key: str,
        src_dir: Path,
        dst_dir: Path,
        db_name_list: list[str],
        logger: Logger = None,
    ):
        super().__init__(src_dir=src_dir, dst_dir=dst_dir, logger=logger)
        self.wx_key = wx_key
        self.db_name_list = db_name_list

    @override
    def decrypt(self, *args, **kwargs):
        self._decrypt_db()

    def _decrypt_db(self) -> None:
        if not self.src_dir.exists():
            self.logger.error("源目录不存在")
            return
        Task = namedtuple("Task", ["src", "dst"])
        tasks = {}

        # 遍历源数据库中的 db 数据库，并存入 cache 中
        for src_path in self.src_dir.rglob("*.db"):
            name = src_path.stem
            if src_path.stem in self.db_name_list:
                dst_db_path = self.dst_dir.joinpath(src_path.name)
                tasks[name] = Task(src=src_path, dst=dst_db_path)
        # 调用 pywxdump 解密
        for k, task in tasks.items():
            if self.wx_key is None:
                # :todo: 语义有点问题
                self.logger.debug(f"[ COPY ] {k} has decrypted, copy it.")
                shutil.copy(*task)
                continue
            self.logger.debug(f"[ DECRYPTED COPY ] {k} is decrypting. then copy.")
            flag, result = decrypt(self.wx_key, *task)
            if not flag:
                self.logger.error(result)


class ImageDecrypter(Decrypter):
    """
    图片解密器
    """

    def __init__(
        self,
        src_dir: Path,
        dst_dir: Path,
        logger: Logger = None,
    ):
        super().__init__(logger=logger, src_dir=src_dir, dst_dir=dst_dir)

    @override
    def decrypt(self, *args, **kwargs):
        begin = kwargs.get("begin", None)
        end = kwargs.get("end", None)
        self._decrypt_images(begin, end)

    def _decrypt_images(self, begin: date = None, end: date = None) -> None:
        """
        将图片文件从缓存中复制出来，重命名为 [主图字节数_缩略图字节数.jpg]
        """
        if begin is None and end is None:
            y_m_list = self.get_months_by_existing_dir()
        else:
            y_m_list = get_months_between_dates(begin, end)

        # 初始化创建路径
        for y_m in y_m_list:
            src_dir = self.src_dir.joinpath(y_m)
            dst_img_dir = self.dst_dir.joinpath(y_m)
            dst_thm_dir = self.dst_dir.joinpath(y_m)
            dst_img_dir.mkdir(exist_ok=True)
            dst_thm_dir.mkdir(exist_ok=True)
            for file in src_dir.rglob("*"):
                if file.is_file() and not file.name.endswith("_t"):
                    self._handle_img(y_m, file)

    def _handle_img(self, year_month: str, file: Path) -> None:
        """
        处理单个文件，解密图片，并重命名（假设都有缩略图）
        """

        # 读取文件
        with open(file, "rb") as f:
            encrypt_img_buf = bytearray(f.read())
        magic = self.guess_image_encoding_magic(encrypt_img_buf)
        if magic is None:
            return
        self.logger.debug(f"[ FIND IMG ] {file.name}")
        thm_src = file.parent.joinpath(file.name + "_t")
        img_size = file.stat().st_size
        thm_size = thm_src.stat().st_size if thm_src.exists() else 0
        # 找到对应缩略图
        img_name = f"{img_size}_{thm_size}.jpg"
        thm_name = f"{img_size}_{thm_size}_t.jpg"
        thm_dst = self.dst_dir.joinpath(year_month, thm_name)
        img_dst = self.dst_dir.joinpath(year_month, img_name)
        # 如果目标目录已存在，则跳过
        if img_dst.exists():
            self.logger.debug(f"[ SKIP IMG/THUMB ]  {img_name}")
            return
        # 读缩略图加密
        if thm_src.exists() and not thm_dst.exists():
            self.logger.info(f"[ HANDLE THUMB ] file name is {thm_name}")
            # 读取加密缩略图
            with open(thm_src, "rb") as f:
                encrypt_thm_buf = bytearray(f.read())
            # 写解密缩略图
            decrypt_thm_buf = self.xor_decode(magic, encrypt_thm_buf)
            with open(thm_dst, "wb") as f:
                f.write(decrypt_thm_buf)
        # 写主图
        decrypt_img_buf = self.xor_decode(magic, encrypt_img_buf)
        with open(img_dst, "wb") as f:
            self.logger.info(f"[ HANDLE IMG ] {img_name}")
            f.write(decrypt_img_buf)

    @staticmethod
    def xor_decode(magic: int, buf: bytes):
        if magic is None:
            raise ValueError("magic cannot be None")
        return bytearray([b ^ magic for b in list(buf)])

    @classmethod
    def guess_image_encoding_magic(cls, buf: bytes):
        header_code, check_code = 0xFF, 0xD8
        # 微信图片加密方法对字节逐一“异或”，即 源文件^magic(未知数)=加密后文件
        # 已知jpg的头字节是0xff，将0xff与加密文件的头字节做异或运算求解magic码
        magic = header_code ^ list(buf)[0] if buf else 0x00
        # 尝试使用magic码解密，如果第二字节符合jpg特质，则图片解密成功
        _, code = cls.xor_decode(magic, buf[:2])
        if check_code == code:
            return magic


class VideoDecrypter(Decrypter):

    def __init__(
        self, src_dir: Path, dst_dir: Path, bin_path: Path, logger: Logger = None
    ):
        super().__init__(src_dir=src_dir, dst_dir=dst_dir, logger=logger)
        self.bin_path = bin_path
        self.src_dir = src_dir
        self.dst_dir = dst_dir
        self.logger = logger or getLogger(__name__)

    @override
    def decrypt(self, *args, **kwargs):
        begin = kwargs.get("begin", None)
        end = kwargs.get("end", None)
        self._handle_videos(begin, end)

    @property
    def ffprobe_path(self):
        return self.bin_path.joinpath("ffprobe.exe")

    @property
    def ffmpeg_path(self):
        return self.bin_path.joinpath("ffmpeg.exe")

    def _handle_videos(self, begin: date = None, end: date = None) -> None:
        """
        将视频文件从缓存中复制出来，重命名为 [md5_duration.mp4]
        """
        if begin is None and end is None:
            y_m_list = self.get_months_by_existing_dir()
        else:
            y_m_list = get_months_between_dates(begin, end)

        for y_m in y_m_list:
            src_dir = self.src_dir.joinpath(y_m)
            dst_dir = self.dst_dir.joinpath(y_m)
            dst_dir.mkdir(exist_ok=True)
            for file in src_dir.rglob("*"):
                file_type = filetype.guess(file)
                if file_type and file_type.extension == "mp4":
                    md5 = self._calculate_md5(file)
                    duration = self._get_video_duration(file)
                    video_dst_path = dst_dir.joinpath(f"{md5}_{duration}.mp4")
                    if not video_dst_path.exists():
                        self.logger.info(f"[ COPY VIDEO ]: {file}")
                        shutil.copy(file.resolve(), video_dst_path)
                    else:
                        self.logger.debug(f"[ SKIP VIDEO ]: {file}")

    def _calculate_md5(self, file: Path):
        with open(file, "rb") as f:
            content = f.read()
        return hashlib.md5(content).hexdigest()

    def _get_video_duration(self, video_path: Path) -> float:
        """获取视频时长"""
        ffprobe_path = self.ffprobe_path
        if not ffprobe_path.exists():
            self.logger.error(f"[ FFPROBE NOT EXIST ]: {ffprobe_path}")
            return 0
        ffprobe_cmd = f'"{ffprobe_path}"  -i "{video_path}" -show_entries format=duration -v quiet -of csv="p=0"'
        p = subprocess.Popen(
            ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        # self.logger.debug(f"ffprobe cmd: {ffprobe_cmd}")
        out, err = p.communicate()
        if len(str(err, "gbk")) > 0:
            self.logger.error(f"[ SUBPROCESS RESULT ] out:{out} err:{str(err, 'gbk')}")
            return 0
        if len(str(out, "gbk")) == 0:
            return 0
        return float(out)
