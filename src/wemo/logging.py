from __future__ import annotations
import logging
from rich.logging import RichHandler



console_handler = RichHandler(rich_tracebacks=True)


# :todo: 需要配置文件输出 Handler
# :todo: 需要提示 app 类型注解（但是会造成循环应用，pytest 会报错）
def create_logger(app) -> logging.Logger:
    logger = logging.getLogger(app.name)

    if app.debug and not logger.level:
        logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    return logger
