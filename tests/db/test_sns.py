from db.sns import Sns, CommentV20, FeedsV20
import pytest


@pytest.fixture
def sns() -> Sns:
    sns = Sns()
    return sns


def test_temp(sns: Sns):
    res = sns.session.get(FeedsV20, "2")
    print(res)


def test_singleton(sns: Sns):
    """测试单例"""
    sns2 = Sns()
    assert sns == sns2


def test_query_all(sns: Sns):
    """测试查询全部"""
    res = sns.query_all(FeedsV20)
    assert res is not None

    res = sns.query_all(CommentV20)
    assert res is not None


def test_insert(sns: Sns):
    """测试插入"""
    pass


def test_update(sns: Sns):
    """测试更新"""
    pass


def test_update_db_by_table(sns: Sns):
    sns.update_db_from_cache_by_table(FeedsV20)
    sns.update_db_from_cache_by_table(CommentV20)


def test_update_db(sns: Sns):
    sns.update_db_from_cache_by_all()
