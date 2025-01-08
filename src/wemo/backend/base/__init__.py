from wemo.backend.base import constant
from wemo.backend.base.logger import config_app_logger


config_app_logger("wemo", log_dir=constant.LOGS_DIR)
