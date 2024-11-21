from datetime import datetime
from logging import Logger
from pathlib import Path
from typing import Optional, override

from wemo.backend.sync.sync import Syncer
from wemo.backend.utils.utils import get_months_between_dates
from wemo.backend.utils.utils import xor_decode
from wemo.backend.utils.utils import guess_image_encoding_magic
from rich.progress import track


class ImgSyncer(Syncer):

    def __init__(self, src_dir: Path, dst_dir: Path, logger: Optional[Logger] = None):
        if src_dir is None or dst_dir is None:
            raise ValueError("Source and destination directories cannot be None")
        super().__init__(src_dir=src_dir, dst_dir=dst_dir, logger=logger)

    @override
    def sync(
        self,
        begin: Optional[datetime] = None,
        end: Optional[datetime] = None,
        *args,
        **kwargs,
    ):
        if begin is None or end is None:
            ym_list = self.get_months_by_existing_dir()
        else:
            ym_list = get_months_between_dates(begin, end)

        for ym in ym_list:
            # ym 是 [2024-10, 2024-11, ...] 诸如此类
            self.logger.debug(f"[ IMG SYNCER ] Dir({ym}) start decrypt.")
            src_ym_dir = self.src_dir.joinpath(ym)
            dst_ym_dir = self.dst_dir.joinpath(ym)
            src_ym_dir.mkdir(parents=True, exist_ok=True)
            dst_ym_dir.mkdir(parents=True, exist_ok=True)
            self._decrypt_img_list_by_ym(src_ym_dir, dst_ym_dir)

    def _decrypt_img_list_by_ym(self, src_ym_dir: Path, dst_ym_dir: Path) -> None:
        """
        将图片文件从缓存中复制出来，重命名为 [主图字节数_缩略图字节数.jpg]
        """
        # 初始化创建路径
        for p in track(
            src_ym_dir.iterdir(),
            description="Decrypting images...",
            total=len(list(src_ym_dir.iterdir())),
        ):
            if p.is_file() and not p.stem.endswith("_t"):
                self._decrypt_img(dst_ym_dir, p)

    def _decrypt_img(self, dst_ym_dir: Path, src_file_path: Path) -> None:
        """
        处理单个文件，解密图片，并重命名（假设都有缩略图）
        """
        # self.logger.debug(f"[ IMG SYNCER ] File({src_file_path.stem}) start decrypt.")
        # 读取文件
        with open(src_file_path, "rb") as f:
            encrypt_img_buf = bytearray(f.read())
        magic = guess_image_encoding_magic(encrypt_img_buf)
        if not magic:
            return
        thm_src = src_file_path.parent.joinpath(src_file_path.stem + "_t")
        img_size = src_file_path.stat().st_size
        thm_size = thm_src.stat().st_size if thm_src.exists() else 0

        # 找到对应缩略图
        img_name = f"{img_size}_{thm_size}.jpg"
        img_dst = dst_ym_dir.joinpath(img_name)
        # 如果目标目录已存在，则跳过
        if not img_dst.exists():
            # 处理 IMG
            decrypt_img_buf = xor_decode(magic, encrypt_img_buf)
            with open(img_dst, "wb") as f:
                self.logger.debug(
                    f"[ IMG SYNCER ] Handle with Dir({dst_ym_dir.name})/Img({img_name})"
                )
                f.write(decrypt_img_buf)
        # 处理 THUMB
        thm_name = f"{img_size}_{thm_size}_t.jpg"
        thm_dst = dst_ym_dir.joinpath(thm_name)
        if thm_src.exists() and not thm_dst.exists():
            self.logger.debug(
                f"[ IMG SYNCER ] Handle with Dir({dst_ym_dir.name})/Thumb({thm_name})"
            )
            # 读取加密缩略图
            with open(thm_src, "rb") as f:
                encrypt_thm_buf = bytearray(f.read())
            # 写解密缩略图
            decrypt_thm_buf = xor_decode(magic, encrypt_thm_buf)
            with open(thm_dst, "wb") as f:
                f.write(decrypt_thm_buf)
