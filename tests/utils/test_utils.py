import datetime
from datetime import date

from wemo.backend.utils.mock import mock_bytes, mock_timestamp, mock_user
from wemo.backend.utils.utils import get_months_between_dates, timestamp_convert


def test_get_months_between_dates():
    begin = date(2024, 1, 1)
    end = date(2024, 12, 1)
    res = get_months_between_dates(begin, end)
    print(res)


def test_timestamp_convert():
    d = timestamp_convert(0)
    assert d.date() == date(1970, 1, 1)
    assert d.time() == datetime.time(8, 0)


def test_date_tools():
    start = date(2020, 1, 1)
    end = date(2021, 12, 19)
    print(get_months_between_dates(start, end))


def test_mock_bytes():
    b1 = mock_bytes()
    b2 = mock_bytes()

    assert b1 != b2


def test_mock_user():
    u1 = mock_user(1)
    u1_other = mock_user(1)
    u2 = mock_user(2)

    assert u1 == u1_other
    assert u1 != u2


def test_mock_timestamp():
    t1 = mock_timestamp()
    t2 = mock_timestamp()

    assert t1 != t2
