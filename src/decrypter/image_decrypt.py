import os
import traceback
from datetime import date
from pathlib import Path

from config import WX_SNS_CACHE_DIR, LOG
from config.user_init import APP_USER_SNS_DIR, WX_DIR
from utils import get_all_month_between_dates
from utils import xor_decode
from utils import guess_image_encoding_magic


class ImageDecrypter:

    def __init__(self):
        self.app_sns_images = APP_USER_SNS_DIR.joinpath("images")
        self.app_sns_thumbs = APP_USER_SNS_DIR.joinpath("thumbs")
        pass

    def decrypt_images(self, start: date, end: date) -> None:
        """将图片文件从缓存中复制出来，重命名为{主图字节数}_{缩略图字节数}.jpg
        duration单位为秒
        """
        year_month_list = get_all_month_between_dates(start, end)

        total_files = 0
        processed_files = 0

        for year_month in year_month_list:
            source_dir = WX_SNS_CACHE_DIR.joinpath(year_month)
            total_files = total_files + len(list(source_dir.rglob("*")))

        for year_month in year_month_list:
            source_dir = WX_SNS_CACHE_DIR.joinpath(year_month)
            for file in source_dir.rglob("*"):
                # 排除缩略图
                if file.is_file() and not file.name.endswith("_t"):
                    try:
                        os.makedirs(
                            self.app_sns_images.joinpath(year_month),
                            exist_ok=True,
                        )
                        os.makedirs(
                            self.app_sns_thumbs.joinpath(year_month),
                            exist_ok=True,
                        )
                        self.handle_file(year_month, file)
                    except Exception:
                        traceback.print_exc()
                processed_files = processed_files + 1

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
        file_name = f"{img_file_size}_{thumb_file_size}_{file.name}.jpg"
        # 找到对应缩略图
        thumb_file = WX_DIR.joinpath(file.name + "_t")
        if thumb_file.exists():
            thumb_file_size = thumb_file.stat().st_size
            # 读缩略图加密
            with open(thumb_file, "rb") as f:
                thumb_buff = bytearray(f.read())
            # 写缩略图
            thumb_des = self.app_sns_thumbs.joinpath(year_month, file_name)

            with open(thumb_des, "wb") as f:
                new_thumb_buff = xor_decode(magic, thumb_buff)
                f.write(new_thumb_buff)

        img_des = self.app_sns_images.joinpath(year_month, file_name)
        with open(img_des, "wb") as f:
            new_buf = xor_decode(magic, buff)
            f.write(new_buf)
