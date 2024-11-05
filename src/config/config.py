import toml
from utils import singleton
from .constant import CONFIG_DIR


@singleton
class Config:

    # 读取 config.toml 文件
    def __init__(self):
        conf = {}
        with open(CONFIG_DIR.joinpath("config.toml"), "r", encoding="utf-8") as f:
            tmp = toml.loads(f.read())
            conf.update(tmp)
        self.conf = conf

    # 获取配置
    def get(self, s: str):
        split = s.split(".")
        res = self.conf
        for item in split:
            res = res.get(item)
            if res is None:
                return None
        return res


config = Config()
