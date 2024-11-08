import pytest

from db import DataBaseSet, MICRO_MSG, MISC, SNS


@pytest.fixture
def dbs():
    dbs = DataBaseSet()
    dbs.init_db_set()
    return dbs


def test_update_dbs(dbs: DataBaseSet):
    dbs.update_user_db_by_cache(MISC)
    dbs.update_user_db_by_cache(SNS)
    dbs.update_user_db_by_cache(MICRO_MSG)

def test_update_sns(dbs: DataBaseSet):
    dbs.update_user_db_by_cache(SNS)
