import datetime
from datetime import date

from utils import get_months_between_dates
from utils.helper import timestamp_convert


def test_timestamp_convert():
    d = timestamp_convert(0)
    assert d.date() == date(1970, 1, 1)
    assert d.time() == datetime.time(8, 0)


def test_date_tools():
    start = date(2020, 1, 1)
    end = date(2021, 12, 19)
    print(get_months_between_dates(start, end))
