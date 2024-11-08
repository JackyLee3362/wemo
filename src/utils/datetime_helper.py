from datetime import datetime, timezone, timedelta, date


def timestamp_convert(timestamp: int):
    dt = datetime.fromtimestamp(timestamp, timezone.utc)
    # 转换为北京时间（UTC+8）
    beijing_timezone = timezone(timedelta(hours=8))
    d = dt.astimezone(beijing_timezone)
    return d


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


def to_timestamp(t):
    if isinstance(t, int):
        return t
    elif isinstance(t, datetime):
        return int(t.timestamp())
    elif isinstance(t, float):
        return int(t)
    elif isinstance(t, date):
        return int(datetime.combine(t, datetime.min.time()).timestamp())
    try:
        if isinstance(t, str) and ":" in t:
            return int(datetime.strptime(t, "%Y-%m-%d %H:%M:%S").timestamp())
        if isinstance(t, str) and "-" in t:
            return int(datetime.strptime(t, "%Y-%m-%d").timestamp())
    except Exception:
        raise ValueError("Invalid timestamp")
    raise TypeError("无法转化为时间戳")
