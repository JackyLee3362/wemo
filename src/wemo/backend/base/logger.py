import logging
from pathlib import Path
from rich.logging import RichHandler
from datetime import datetime


default_log_fmt = "[%(asctime)s] %(levelname)-8s - %(name)s %(funcName)s  : %(message)s"
default_date_fmt = "%Y-%m-%d %H:%M:%S"
default_file_fmt = "%Y-%m-%d.log"
console_handler = RichHandler(rich_tracebacks=True)


def config_app_logger(
    name: str,
    level=logging.DEBUG,
    log_dir: str = None,
    log_fmt=None,
    date_fmt=None,
    file_fmt=None,
):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(console_handler)
    _log_fmt = log_fmt or default_log_fmt
    _date_fmt = date_fmt or default_date_fmt
    _file_fmt = file_fmt or default_file_fmt
    formatter = logging.Formatter(fmt=_log_fmt, datefmt=_date_fmt)
    # console_handler.setFormatter(formatter)
    # 添加文件日志器
    if log_dir:
        log_name_fmt = datetime.now().strftime(_file_fmt)
        log_dir_obj = Path(log_dir)
        log_dir_obj.mkdir(parents=True, exist_ok=True)
        log_file_path = log_dir_obj.joinpath(log_name_fmt)
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
