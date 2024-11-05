import logging
import datetime
from rich.logging import RichHandler

from .config import config
from .constant import LOG_DIR

# 读取配置
logging_name = config.get("logging.name")
logging_level = config.get("logging.level")
logging_dir = LOG_DIR
# 设置日志
LOG = logging.getLogger(logging_name)
LOG.setLevel(logging_level)

# 控制台输出
console_handler = RichHandler(level=logging_level, rich_tracebacks=True)
LOG.addHandler(console_handler)

# 文件输出
date = datetime.datetime.now().strftime("%Y-%m-%d")
file_handler = logging.FileHandler(filename=LOG_DIR / date, encoding="utf-8")
LOG.addHandler(file_handler)
