import logging
import time
from pathlib import Path

from rich.console import Console
from rich.progress import track

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console = Console(color_system=None, stderr=None)


def work(i):
    # logger.info("Working: {}", i)
    time.sleep(0.05)


def main():
    logger.info("Before", "123")
    # with Progress(console=console) as progress:
    #     for i in progress.track(range(100)):
    #         work(i)
    p = Path(r"E:\Project\WechatMomentsBackup\data\wxid_h8cex1v6segm21\data\image")

    for item in track(
        p.iterdir(), description="Processing...", total=len(list(p.iterdir()))
    ):
        work(item)
    logger.info("After")


if __name__ == "__main__":

    # We need to specify end=''" as log message already ends with \n (thus the lambda function)
    # Also forcing 'colorize=True' otherwise Loguru won't recognize that the sink support colors

    main()
