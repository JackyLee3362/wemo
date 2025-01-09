import logging
import shutil
from collections import namedtuple
from pathlib import Path

from wemo.backend.sync.sync import Syncer
from wemo.backend.utils.helper import decrypt

logger = logging.getLogger(__name__)


class DBSyncer(Syncer):
    """
    数据库解密器
    """

    def __str__(self):
        return "[ DECRYPT ]"

    def __init__(
        self,
        wx_key: str,
        src_dir: Path,
        dst_dir: Path,
        db_name_list: list[str],
    ):
        super().__init__(src_dir=src_dir, dst_dir=dst_dir)
        self.wx_key = wx_key
        self.db_name_list = db_name_list

    def sync(self, *args, **kwargs):
        self._decrypt_db()

    def _decrypt_db(self) -> None:
        if not self.src_dir.exists():
            logger.warning("[ DECRYPT ] src dir not exists.")
            return
        Task = namedtuple("Task", ["src", "dst"])
        tasks: dict[str, Task] = {}

        # 遍历源数据库中的 db 数据库，并存入 cache 中
        for src_path in self.src_dir.rglob("*.db"):
            name = src_path.stem
            if src_path.stem in self.db_name_list:
                dst_db_path = self.dst_dir.joinpath(src_path.name)
                tasks[name] = Task(src=src_path, dst=dst_db_path)
        # 调用 pywxdump 解密
        for k, task in tasks.items():
            if self.wx_key is None:
                logger.debug(f"{self} db({k}) is None, only copy.")
                shutil.copy(task.src, task.dst)
                continue
            logger.debug(f"{self} db({k}) exists, decrypt and copy.")
            flag, result = decrypt(self.wx_key, task.src, task.dst)
            if not flag:
                logger.warning(result)
