from __future__ import annotations

from logging import Logger, getLogger
import logging
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from sqlalchemy.schema import MetaData


class UserTable(DeclarativeBase):
    @staticmethod
    def mock(seed: int) -> UserTable:
        raise NotImplementedError()


class AbsUserDB:

    def __init__(self, db_url: str, db_name: str = None, logger: Logger = None):
        self.logger = logger or getLogger(__name__)
        db_name = db_name or self.__class__.__name__
        self.db_name = db_name
        self.logger.debug(f"[ DB INIT ] {db_name}")
        self.db_url = db_url
        self.table_cls_list: list[UserTable] = []
        self.engine = None
        self.db_session = None
        self.session: Session = None
        self.metadata = None

    def init_db(self):
        """初始化数据库
        1. 连接数据库
        2. 建立会话
        3. 创建表
        """
        self.connect_db()
        self.build_session()
        self.create_tables()

    def create_tables(self):
        if not self.engine:
            self.connect_db()
        self.metadata = MetaData()
        self.metadata.create_all(
            bind=self.engine, tables=[t.__table__ for t in self.table_cls_list]
        )

    def connect_db(self):
        self.logger.debug(f"[ DB CONNECT ] {self.db_name} ")
        self.engine = create_engine(f"sqlite:///{self.db_url}", echo=False)
        self.build_session()

    def build_session(self):
        self.logger.debug(f"[ SESSION BUILD ] {self.db_name}")
        self.db_session = sessionmaker(bind=self.engine)
        self.session = self.db_session()

    def register_tables(self, table_cls_list: list) -> None:
        self.table_cls_list.extend(table_cls_list)

    def query_all(self, table_cls: UserTable):
        data = self.session.query(table_cls).all()
        self.logger.debug(f"[ QUERY ALL ] {table_cls.__name__} count is {len(data)}")
        return data

    def count_all(self, table_cls: UserTable) -> int:
        cnt = self.session.query(table_cls).count()
        self.logger.debug(f"[ COUNT ALL ] {table_cls.__name__} count is {cnt}")
        return cnt

    def insert_all(self, data_list: list[UserTable]) -> None:
        if len(data_list) < 0:
            return
        self.logger.debug(f"[ INSERT ALL ] {data_list[0].__class__.__tablename__}")
        for d in data_list:
            self.session.add(d)
        self.session.commit()

    def merge_all(self, data_list: list[UserTable]) -> None:
        if len(data_list) <= 0:
            return
        self.logger.debug(f"[ MERGE ALL ] {data_list[0].__class__.__tablename__}")
        for d in data_list:
            self.session.merge(d)
        self.session.commit()

    def close_session(self) -> None:
        self.logger.debug(f"[ SESSION CLOSED ] {self.db_name}")
        self.session.close()


class DbCacheSet:
    def __init__(self, db: AbsUserDB, cache: AbsUserDB, logger=None):
        self.db = db
        self.cache = cache
        if db.db_name != cache.db_name:
            raise ValueError("db_name 不一致")
        self.name = db.db_name
        self.logger = logger or logging.getLogger(__name__)

    def init_db_cache(self):
        self.logger.info(f"[ INIT DB/CACHE SET ] {self.name}")
        self.db.init_db()
        self.cache.init_db()

    def update_db_by_cache(self):
        for t_cls in self.db.table_cls_list:
            self.logger.info(f"[ UPDATE DB BY CACHE ] {t_cls.__name__}")
            data_list = self.cache.query_all(t_cls)
            self.db.merge_all(data_list)
