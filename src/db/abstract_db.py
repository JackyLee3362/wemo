from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from common import LOG

Base = declarative_base()


class AbstractUserDB:
    def __init__(self, db_dir: Path, db_name: str):
        LOG.debug(f"[{db_name}]: 初始化数据库")
        self.db_name = db_name
        self.db_url = db_dir.joinpath(db_name + ".db")
        self.tables = []
        self.engine = None
        self.db_session = None
        self.session = None

    def connect_db(self):
        LOG.debug(f"[{self.db_name}]: 连接数据库 {self.db_url} 建立会话")
        self.engine = create_engine(f"sqlite:///{self.db_url}")
        self.db_session = sessionmaker(bind=self.engine)
        self.session = self.db_session()

    def register_tables(self, table_cls_list: list) -> None:
        self.tables.extend(table_cls_list)

    def query_all(self, table_cls):
        return self.session.query(table_cls).all()

    def count_all(self, table_cls):
        return self.session.query(table_cls).count()

    def insert_all(self, data: list, table_cls) -> None:
        for d in data:
            self.insert_one(d, table_cls)

    def insert_one(self, src, table_cls) -> None:
        dst = table_cls()
        for column in table_cls.__table__.columns:
            setattr(dst, column.name, getattr(src, column.name))
        self.session.add(dst)
        self.session.commit()

    def update_one(self, d1, d2, table_cls) -> None:
        for column in table_cls.__table__.columns:
            setattr(d1, column.name, getattr(d2, column.name))
        self.session.commit()

    def update_all(self, data: list, table_cls) -> None:
        for d1, d2 in data:
            self.update_one(d1, d2, table_cls)

    def close_session(self) -> None:
        LOG.debug(f"[{self.db_name}] 关闭连接")
        self.session.close()
