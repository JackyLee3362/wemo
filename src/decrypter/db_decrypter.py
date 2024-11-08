import shutil
from pathlib import Path
from pywxdump import decrypt
from collections import namedtuple
from logging import Logger

from .decrypter import Decrypter


class DatabaseDecrypter(Decrypter):
    """
    数据库解密器
    """

    def __init__(
        self,
        key: str = "",
        src_dir: Path = None,
        dst_dir: Path = None,
        db_name_list: list[str] = [],
        has_decrypt: bool = False,
        logger: Logger = None,
    ):
        super().__init__(src_dir=src_dir, dst_dir=dst_dir, logger=logger)
        self.key = key
        self.db_name_list = db_name_list
        self.has_decrypt = has_decrypt

    def decrypt_and_copy(self):
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
            if self.has_decrypt:
                self.logger.debug(f"[{k}] 数据库已解密，复制数据库")
                shutil.copy(*task)
                continue
            self.logger.debug(f"[{k}] 开始解密，并复制数据库")
            flag, result = decrypt(self.key, *task)
            if not flag:
                self.logger.error(result)
