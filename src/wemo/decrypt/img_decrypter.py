from datetime import date
from logging import Logger
from pathlib import Path
from typing import override

from wemo.decrypt.decrypter import Decrypter
from wemo.utils.utils import get_months_between_dates


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
        # self.logger.debug(f"[ FIND IMG ] {file.name}")
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
            # self.logger.debug(f"[ SKIP IMG/THUMB ]  {img_name}")
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
