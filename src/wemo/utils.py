import time
import os
from datetime import datetime, timezone, timedelta, date
from functools import wraps
import random
import uuid

random.seed(42)


def get_months_between_dates(start: date, end: date) -> list[str]:
    if start > end:
        raise ValueError("Start date must be before end date.")

    months = []
    current = start.replace(day=1)  # Start from the first day of the start month

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
    return f"https://example.com/{random.randint(0, 10000)}"


def mock_user(n):
    return f"wxid_{n}"


def mock_bytes(size=1024):
    return bytes(random.getrandbits(8) for _ in range(size))


def mock_timestamp():
    return int(time.time()) + random.randint(0, 100000)


def mock_sns_content():
    return ""
