from __future__ import annotations

from ast import Return
from logging import Logger, getLogger
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.schema import MetaData


class UserTable(DeclarativeBase):
    @staticmethod
    def mock(seed: int) -> UserTable:
        raise NotImplementedError()


class AbsUserDB:

    def __init__(self, db_dir: Path, db_name: str = None, logger: Logger = None):
        self.logger = logger or getLogger(__name__)
        db_name = db_name or self.__class__.__name__
        self.db_name = db_name
        self.logger.debug(f"[ DB INIT ] {db_name}")
        self.db_url = db_dir.joinpath(db_name + ".db")
        self.table_cls_list: list[UserTable] = []
        self.engine = None
        self.db_session = None
        self.session = None
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

    def build_session(self):
        self.logger.debug(f"[ SESSION BUILD ] {self.db_name}")
        self.db_session = sessionmaker(bind=self.engine)
        self.session = self.db_session()

    def register_tables(self, table_cls_list: list) -> None:
        self.table_cls_list.extend(table_cls_list)

    def query_all(self, table_cls: UserTable):
        data = self.session.query(table_cls).all()
        self.logger.debug(f"[ QUERY ALL ] {table_cls.__name__} :: CNT = {len(data)}")
        return data

    def count_all(self, table_cls: UserTable) -> int:
        cnt = self.session.query(table_cls).count()
        self.logger.debug(f"[ COUNT ALL ] {table_cls.__name__} :: CNT = {cnt}")
        return cnt

    def insert_all(self, data_list: list[UserTable]) -> None:
        if len(data_list) < 0:
            return
        self.logger.debug(f"[ INSERT ALL ] {data_list[0].__class__.__tablename__}")
        for d in data_list:
            self.session.add(d)
        self.session.commit()

    def merge_all(self, data_list: list[UserTable]) -> None:
        if len(data_list) < 0:
            return
        self.logger.debug(f"[ MERGE ALL ] {data_list[0].__class__.__tablename__}")
        for d in data_list:
            self.session.merge(d)
        self.session.commit()

    def close_session(self) -> None:
        self.logger.debug(f"[ SESSION CLOSED ] {self.db_name}")
        self.session.close()
