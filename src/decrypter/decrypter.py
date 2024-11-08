from datetime import date
from logging import Logger, getLogger
from pathlib import Path


class Decrypter:
    def __init__(
        self,
        src_dir: Path = None,
        dst_dir: Path = None,
        logger: Logger = None,
    ):
        self.logger = logger or getLogger(__name__)
        self.src_dir = src_dir
        self.dst_dir = dst_dir

    def get_months_between_dates(start: date, end: date) -> list[str]:
        result = []
        cur: date = start
        while cur <= end:
            # 打印当前日期的年份和月份
            result.append(cur.strftime("%Y-%m"))
            year = cur.year + (cur.month // 12)
            month = cur.month % 12 + 1
            # 更新current_date到下个月的第一天
            cur = date(year, month, 1)
        return result
