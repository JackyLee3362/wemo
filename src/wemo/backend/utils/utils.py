import math
import random
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

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


def find_video_by_md5_or_duration(path: Path, md5: str, duration: float) -> Path | None:
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


def find_img_thumb_by_url(path: Path, urn: str) -> tuple[Path | None, Path | None]:
    dst_path = path.joinpath(urn)
    if not dst_path.exists():
        return None, None
    img_path = thm_path = None
    # 如果不存在，跳过
    # 否则遍历文件夹
    total_res = list(dst_path.iterdir())
    if len(total_res) == 1:
        return total_res[0], total_res[0]
    for item in dst_path.iterdir():
        if item.suffix == ".jpg":
            if not item.stem.endswith("_t"):
                img_path = item
            elif item.stem.endswith("_t"):
                thm_path = item
    return img_path, thm_path


def xor_decode(magic: int, buf: bytearray):
    return bytearray([b ^ magic for b in list(buf)])


def guess_image_encoding_magic(buf: bytearray):
    """微信图片加密方法对字节逐一异或
    即是
        源文件 ^ magic(未知数) = 加密后文件
    jpg 的头字节是 0xFF， 0xD8
    0xFF 与加密文件的头字节做异或运算求解 magic
    尝试使用 magic 码解密，如果第二字节 == 0xD8，则解密成功
    """
    jpg_1 = 0xFF
    jpg_2 = 0xD8
    xor_1 = buf[0] ^ jpg_1
    xor_2 = buf[1] ^ jpg_2
    if xor_1 == xor_2:
        return xor_1
    return 0
