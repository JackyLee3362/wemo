from __future__ import annotations
from functools import cache
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from pathlib import Path

from config import LOG

Base = declarative_base()


class UserDB:
    def __init__(self, wxid, db_name):
        LOG.info(f"初始化数据库: {wxid}-{db_name}")
        self.wxid = wxid
        self.db_name = db_name
        self.name = db_name
        self.db_path = Path(f"db/{wxid}/{db_name}.db")
        self.db_cache_path = Path(f"db/{wxid}/cache/{db_name}.db")
        self.table = set()

    def connect(self):
        LOG.info(f"连接数据库: {self.db_name}")
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        self.DBSession = sessionmaker(bind=self.engine)

    def query_cache_by_table(self, table) -> list:
        LOG.info(f"连接缓存数据库: {self.db_name}")
        cache_engine = create_engine(f"sqlite:///{self.db_cache_path}")
        DBSession = sessionmaker(bind=cache_engine)
        session = DBSession()
        res = session.query(table).all()
        session.close()
        return res

    def init_session(self) -> None:
        self.session = self.DBSession()

    def register_table(self, table) -> None:
        self.table.add(table)

    def query_all(self, tableCls):
        return self.session.query(tableCls).all()

    def count_all(self, tableCls):
        res = self.session.query(tableCls).count()
        return res

    def insert_all(self, data: list, tableCls) -> None:
        for d in data:
            self.insert_one(d, tableCls)

    def insert_one(self, src, tableCls) -> None:
        dst = tableCls()
        for column in tableCls.__table__.columns:
            setattr(dst, column.name, getattr(src, column.name))
        self.session.add(dst)
        self.session.commit()

    def update_one(self, d1, d2, tableCls) -> None:
        for column in tableCls.__table__.columns:
            setattr(d1, column.name, getattr(d2, column.name))
        self.session.commit()

    def _update_all(self, data: list, tableCls):
        # 检查
        for d1, d2 in data:
            self.update_one(d1, d2, tableCls)

    def to_dict(self, data: list) -> dict:
        return {obj.__hash__(): obj for obj in data}

    def _data_for_insert(self, db: dict, cache: dict) -> list:
        # 输入验证
        if not isinstance(db, dict) or not isinstance(cache, dict):
            raise TypeError("Both 'user' and 'cache' must be dictionaries.")
        # 获取 cache 中不存在于 user 中的键
        keys = cache.keys() - db.keys()
        return [cache[k] for k in keys]

    def _data_for_update(self, db: dict, cache: dict) -> list:
        # 检查 user 和 cache 是否为空
        if not db or not cache:
            return []

        # 检查 user 和 cache 是否为字典类型
        if not isinstance(db, dict) or not isinstance(cache, dict):
            raise TypeError("Both user and cache must be dictionaries")

        # 使用字典的 items() 方法直接进行比较
        res = []
        for k, v in db.items():
            if k in cache and v != cache[k]:
                res.append([v, cache[k]])

        return res

    def close_session(self) -> None:
        LOG.info(f"关闭连接: {self.name}")
        self.session.close()

    def update_db_from_cache_by_table(self, tableCls):
        LOG.info(f"更新数据表: {tableCls.__name__}")
        # 获取字典
        db_data = self.query_all(tableCls)
        LOG.info(f"主数据量: {len(db_data)}")
        cache_data = self.query_cache_by_table(tableCls)
        LOG.info(f"缓存数据量: {len(cache_data)}")
        cache_dict: dict = self.to_dict(cache_data)
        db_dict: dict = self.to_dict(db_data)
        # 计算需要更新的数据
        insert_data = self._data_for_insert(db_dict, cache_dict)
        LOG.info(f"新增数据量: {len(insert_data)}")
        update_data = self._data_for_update(db_dict, cache_dict)
        LOG.info(f"更新数据量: {len(update_data)}")
        # 更新数据
        self.insert_all(insert_data, tableCls)
        self._update_all(update_data, tableCls)

    def bulk_save(self, tableCls):
        cache_data = self.query_cache_by_table(tableCls)
        self.session.bulk_save_objects(cache_data)
        self.session.commit()

    def update_db_from_cache_by_all(self):
        LOG.info(f"全量更新: {self.db_name}")
        for table in self.table:
            before = self.count_all(table)
            self.update_db_from_cache_by_table(table)
            after = self.count_all(table)
            LOG.info(f"表数据更新 {table.__name__}: {before} -> {after}")
