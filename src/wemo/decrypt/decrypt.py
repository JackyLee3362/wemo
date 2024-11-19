import hashlib
import logging
from pathlib import Path

from wemo.model.ctx import Context
from wemo.utils.utils import guess_image_encoding_magic, xor_decode


class Decrypt:
    def __init__(self, ctx: Context, src_dir: Path, logger=None):
        self.logger = logger or ctx.logger or logging.getLogger(__name__)
        self.src_dir = src_dir

    def load_data(self, filename: str) -> bytes:
        p = self.src_dir.joinpath(filename)
        with open(p, "rb") as f:
            return f.read()

    def cal_data_md5(self, data: bytes) -> str:
        return hashlib.md5(data).hexdigest()

    def encrypt_name(self, name: str) -> str:
        return hashlib.md5(name.encode()).hexdigest()

    def encrypt_data(self, data: bytes) -> bytes:
        d = bytearray(data)
        magic = guess_image_encoding_magic(d)
        res = xor_decode(magic, d)
        return bytes(res)