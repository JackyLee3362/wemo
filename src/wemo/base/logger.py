from __future__ import annotations
import logging
from pathlib import Path
from rich.logging import RichHandler
from datetime import datetime

time_fmt = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(
    fmt="[%(asctime)s] %(levelname)-8s %(filename)s : %(message)s",
    datefmt=time_fmt,
)

log_name = datetime.now().strftime("%Y-%m-%d.log")
console_handler = RichHandler(rich_tracebacks=True)


# :todo: 需要提示 app 类型注解（但是会造成循环应用，pytest 会报错）
def create_app_logger(app, log_dir: Path = None) -> logging.Logger:
    logger = logging.getLogger(app.name)

    if app.debug and not logger.level:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    # 添加文件日志器
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file_path = log_dir.joinpath(log_name)
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def default_console_logger(name) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    return logger
