import time

import logging
from rich.console import Console
from rich.progress import Progress
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console = Console(color_system=None, stderr=None)


def work(i):
    # logger.info("Working: {}", i)
    time.sleep(0.05)


def main():
    logger.info("Before", "123")
    with Progress(console=console) as progress:
        for i in progress.track(range(100)):
            work(i)
    logger.info("After")


if __name__ == "__main__":

    # We need to specify end=''" as log message already ends with \n (thus the lambda function)
    # Also forcing 'colorize=True' otherwise Loguru won't recognize that the sink support colors

    main()
