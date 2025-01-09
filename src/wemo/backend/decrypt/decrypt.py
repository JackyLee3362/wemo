import hashlib
import logging
from pathlib import Path

from wemo.backend.ctx import AppContext
from wemo.backend.utils.utils import guess_image_encoding_magic, xor_decode

logger = logging.getLogger(__name__)


class Decrypt:
    def __init__(self, ctx: AppContext, src_dir: Path):
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
