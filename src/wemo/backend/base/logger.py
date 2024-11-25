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


def create_app_logger(
    name: str, level=logging.DEBUG, log_dir: Path = None
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(console_handler)
    # 添加文件日志器
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file_path = log_dir.joinpath(log_name)
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger
