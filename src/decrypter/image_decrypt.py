import os
from datetime import date
from pathlib import Path

from common import RC, LOG
from utils import get_months_between_dates
from utils import xor_decode
from utils import guess_image_encoding_magic


class ImageDecrypter:

    def __init__(self):
        self.app_sns_cache_img = RC.USER_CACHE_SNS_IMAGE
        self.app_sns_cache_thumb = RC.USER_CACHE_SNS_THUMB

    def decrypt_images(self, start: date, end: date) -> None:
        """将图片文件从缓存中复制出来，重命名为{主图字节数}_{缩略图字节数}.jpg
        duration单位为秒
        """
        year_month_list = get_months_between_dates(start, end)

        # 初始化创建路径
        for year_month in year_month_list:
            source_dir = RC.WX_SNS_CACHE_DIR.joinpath(year_month)
            os.makedirs(
                self.app_sns_cache_img.joinpath(year_month),
                exist_ok=True,
            )
            os.makedirs(
                self.app_sns_cache_thumb.joinpath(year_month),
                exist_ok=True,
            )

        for year_month in year_month_list:
            source_dir = RC.WX_SNS_CACHE_DIR.joinpath(year_month)
            for file in source_dir.rglob("*"):
                # 排除缩略图
                if file.is_file() and not file.name.endswith("_t"):
                    self.handle_file(year_month, file)

    def handle_file(self, year_month: str, file: Path):
        # 读取文件
        with open(file, "rb") as f:
            buff = bytearray(f.read())
        magic = guess_image_encoding_magic(buff)
        if magic is None:
            # LOG.error("文件 %s 无法识别，请检查是否为图片文件" % file.name)
            return
        img_file_size = file.stat().st_size
        thumb_file_size = 0
        # 找到对应缩略图
        thumb_file = file.parent.joinpath(file.name + "_t")
        if thumb_file.exists():
            thumb_file_size = thumb_file.stat().st_size
        image_file_name = f"{img_file_size}_{thumb_file_size}.jpg"
        thumb_file_name = f"{img_file_size}_{thumb_file_size}_t.jpg"
        thumb_des = self.app_sns_cache_thumb.joinpath(year_month, thumb_file_name)
        img_des = self.app_sns_cache_img.joinpath(year_month, image_file_name)

        # 读缩略图加密
        if thumb_file.exists() and not thumb_des.exists():
            LOG.info(f"处理 Thumb 文件：{thumb_file_name}")
            with open(thumb_file, "rb") as f:
                thumb_buff = bytearray(f.read())
            # 解密缩略图
            new_thumb_buff = xor_decode(magic, thumb_buff)
            with open(thumb_des, "wb") as f:
                f.write(new_thumb_buff)
        else:
            LOG.debug(f"跳过 Thumb 文件：{thumb_file_name}")
        # 写主图
        new_buf = xor_decode(magic, buff)
        if not img_des.exists():
            with open(img_des, "wb") as f:
                LOG.info(f"处理 Image 文件：{image_file_name}")
                f.write(new_buf)
        else:
            LOG.debug(f"跳过 Image 文件：{image_file_name}")
