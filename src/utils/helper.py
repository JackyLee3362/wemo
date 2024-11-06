from datetime import datetime, timezone, timedelta, date


def timestamp_convert(timestamp: int):
    dt = datetime.fromtimestamp(timestamp, timezone.utc)
    # 转换为北京时间（UTC+8）
    beijing_timezone = timezone(timedelta(hours=8))
    d = dt.astimezone(beijing_timezone)
    return d


def get_all_month_between_dates(start: date, end: date) -> list[str]:
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


def xor_decode(magic, buf):
    return bytearray([b ^ magic for b in list(buf)])


def guess_image_encoding_magic(buf):
    header_code, check_code = 0xFF, 0xD8
    # 微信图片加密方法对字节逐一“异或”，即 源文件^magic(未知数)=加密后文件
    # 已知jpg的头字节是0xff，将0xff与加密文件的头字节做异或运算求解magic码
    magic = header_code ^ list(buf)[0] if buf else 0x00
    # 尝试使用magic码解密，如果第二字节符合jpg特质，则图片解密成功
    _, code = xor_decode(magic, buf[:2])
    if check_code == code:
        return magic
