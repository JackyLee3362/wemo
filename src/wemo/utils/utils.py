import math
import random
import re
import time
from datetime import datetime, timezone, timedelta, date
from functools import wraps
from pathlib import Path
import os


random.seed(42)


def get_months_between_dates(start: date, end: date) -> list[str]:
    if start > end:
        raise ValueError("Start date must be before end date.")

    months = []
    # Start from the first day of the start month
    current = start.replace(day=1)

    while current <= end:
        month_name = current.strftime("%Y-%m")  # Get the full month name
        if month_name not in months:
            months.append(month_name)
        # Move to the next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    return months


def timestamp_convert(timestamp: int):
    dt = datetime.fromtimestamp(timestamp, timezone.utc)
    # 转换为北京时间（UTC+8）
    beijing_timezone = timezone(timedelta(hours=8))
    d = dt.astimezone(beijing_timezone)
    return d


def to_timestamp(t):
    if isinstance(t, (int, float)):
        return int(t)
    elif isinstance(t, datetime):
        return int(t.timestamp())
    elif isinstance(t, date):
        return int(datetime.combine(t, datetime.min.time()).timestamp())

    if isinstance(t, str):
        try:
            if ":" in t:
                return int(datetime.strptime(t, "%Y-%m-%d %H:%M:%S").timestamp())
            elif "-" in t:
                return int(datetime.strptime(t, "%Y-%m-%d").timestamp())
        except ValueError:
            raise ValueError("Invalid timestamp format")

    raise TypeError("Cannot convert to timestamp")


def singleton(cls):
    instance = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instance:
            instance[cls] = cls(*args, **kwargs)
        return instance[cls]

    return get_instance


def run_once(func):
    has_run = False

    def wrapper(*args, **kwargs):
        nonlocal has_run
        if not has_run:
            has_run = True
            return func(*args, **kwargs)

    return wrapper


def mock_url(n):
    return f"https://example.com/{n}"


def mock_user(n):
    return f"wxid_{n}"


def mock_bytes(size=1024):
    return bytes(random.getrandbits(8) for _ in range(size))


def mock_timestamp():
    return int(time.time()) + random.randint(0, 100000)


def mock_sns_content():
    return ""


def find_video_by_md5_or_duration(path: Path, md5: str, duration: float) -> Path:
    """
    使用 MD5 和 视频 匹配视频
    """
    p1 = re.compile(r"^(.*?)(?=_)")
    p2 = re.compile(r"_([0-9.]+)\.mp4")
    round_duration = round(float(duration), 2)

    for file_path in path.iterdir():
        # 使用 md5 匹配视频
        m1 = p1.search(file_path.name)
        if m1 and m1.group() == md5:
            return file_path
        # 使用视频时长匹配视频
        m2 = p2.search(file_path.name)
        if m2 is None:
            continue
        filename_duration = float(m2.group(1))
        if math.isclose(filename_duration, round_duration, abs_tol=0.005):
            return file_path


def find_img_thumb_by_url(path: Path, url: str) -> tuple[Path, Path]:
    dst_path = path.joinpath(url)
    if not dst_path.exists():
        return None, None
    img_path = thm_path = None
    # 如果不存在，跳过
    # 否则遍历文件夹
    for idx, item in enumerate(dst_path.iterdir()):
        if item.suffix == ".jpg":
            if not item.stem.endswith("_t"):
                img_path = item
            if item.stem.endswith("_t"):
                thm_path = item
        # if idx >= 2:
        #     raise FileExistsError("文件过多")
    return img_path, thm_path


def get_debug_flag() -> bool:
    val = os.environ.get("WEMO_DEBUG")
    return bool(val and val.lower() not in {"0", "false", "no"})
