from __future__ import annotations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from pathlib import Path

from config import LOG

Base = declarative_base()


class UserTable:
    def update(self, obj: UserTable):
        raise NotImplementedError("not implemented")


class UserDB:
    def __init__(self, wxid, name):
        self.wxid = wxid
        self.db_path = Path(f"db/{wxid}/{name}.db")
        self.db_cache_path = Path(f"db/{wxid}/cache/{name}.db")
        self.table = set()

    def connect(self):
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        LOG.info(f"连接情况: {self.engine.connect()}")

        self.DBSession = sessionmaker(bind=self.engine)

    def query_cache_by_table(self, table) -> list:
        cache_engine = create_engine(f"sqlite:///{self.db_cache_path}")
        DBSession = sessionmaker(bind=cache_engine)
        session = DBSession()
        res = session.query(table).all()
        DBSession.close_all()
        return res

    def init_session(self) -> None:
        self.session = self.DBSession()

    def register_table(self, table) -> None:
        self.table.add(table)

    def query_all(self, tableCls):
        return self.session.query(tableCls).all()

    def insert_all(self, data: list) -> None:
        self.session.add_all(data)
        self.session.commit()

    def update_one(self, data: UserTable, data2: UserTable) -> None:
        return data.update(data2)

    def update_all(self, data: list):
        for d1, d2 in data:
            self.update_one(d1, d2)
        self.session.commit()

    def to_dict(self, data: list) -> dict:
        return {obj.__hash__(): obj for obj in data}

    def data_for_insert(self, db: dict, cache: dict) -> list:
        # 输入验证
        if not isinstance(db, dict) or not isinstance(cache, dict):
            raise TypeError("Both 'user' and 'cache' must be dictionaries.")
        # 获取 cache 中不存在于 user 中的键
        keys = cache.keys() - db.keys()
        return [cache[k] for k in keys]

    def data_for_update(self, db: dict, cache: dict) -> list:
        # 检查 user 和 cache 是否为空
        if not db or not cache:
            return []

        # 检查 user 和 cache 是否为字典类型
        if not isinstance(db, dict) or not isinstance(cache, dict):
            raise TypeError("Both user and cache must be dictionaries")

        # 使用字典的 items() 方法直接进行比较
        res = [[v, cache[k]] for k, v in db.items() if k in cache and v != cache[k]]

        return res

    def close_session(self) -> None:
        self.session.close()

    def update_db_from_cache_by_table(self, table):
        # 获取字典
        cache_data: dict = self.to_dict(self.query_cache_by_table(table))
        db_data: dict = self.to_dict(self.query_all(table))
        # 计算需要更新的数据
        insert_data = self.data_for_insert(db_data, cache_data)
        update_data = self.data_for_update(db_data, cache_data)
        # 更新数据
        self.insert_all(insert_data)
        self.update_all(update_data)

    def update_db_from_cache(self):
        for table in self.table:
            self.update_db_from_cache_by_table(table)
