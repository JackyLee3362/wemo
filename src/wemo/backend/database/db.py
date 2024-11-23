from __future__ import annotations

from logging import Logger, getLogger
import os

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
        self.logger.debug(f"[ DB ] db({db_name}) init.")
        self.db_url = db_url
        self.table_cls_list: list[UserTable] = []
        self.engine = None
        self.db_session = None
        self.session: Session = None
        self.metadata = None

    def init(self):
        """初始化数据库
        1. 连接数据库
        2. 建立会话
        3. 创建表
        """
        # self.clear_shm_wal()
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

    # def clear_shm_wal(self):
    #     url = str(self.db_url)
    #     shm_url = url + "-shm"
    #     wal_url = url + "-wal"
    # if os.path.exists(shm_url):
    #     self.logger.debug(f"[ DB ] clear shm({self.db_name}-shm).")
    #     os.remove(shm_url)
    # if os.path.exists(wal_url):
    #     self.logger.debug(f"[ DB ] clear wal({self.db_name}-wal).")
    #     os.remove(wal_url)

    def connect_db(self):
        self.logger.debug(f"[ DB ] db({self.db_name}) is connected.")
        url = f"sqlite:///{self.db_url}"
        self.engine = create_engine(url, echo=False)

    def build_session(self):
        self.logger.debug(f"[ DB ] db({self.db_name}) session is build.")
        self.db_session = sessionmaker(bind=self.engine)
        self.session = self.db_session()

    def register_tables(self, table_cls_list: list) -> None:
        self.table_cls_list.extend(table_cls_list)

    def query_all(self, table_cls: UserTable):
        data = self.session.query(table_cls).all()
        self.logger.debug(
            f"[ DB ] db({self.db_name}).table({table_cls.__name__}) query all and count({len(data)})."
        )
        return data

    def count_all(self, table_cls: UserTable) -> int:
        cnt = self.session.query(table_cls).count()
        self.logger.debug(
            f"[ DB ] db({self.db_name}).table({table_cls.__name__}) count({cnt})."
        )
        return cnt

    def insert_all(self, data_list: list[UserTable]) -> None:
        if len(data_list) < 0:
            return
        self.logger.debug(
            f"[ DB ] db({self.db_name}).table({data_list[0].__class__.__name__}) inserting..."
        )
        for d in data_list:
            self.session.add(d)
        self.session.commit()

    def merge_all(self, data_list: list[UserTable]) -> None:
        if len(data_list) <= 0:
            return
        self.logger.debug(
            f"[ DB ] db({self.db_name}).table({data_list[0].__class__.__name__}) merging..."
        )
        for d in data_list:
            self.session.merge(d)
        self.session.commit()

    def close_session(self) -> None:
        self.logger.debug(f"[ DB ] db({self.db_name}) session closed.")
        self.session.close()

    def close_connection(self) -> None:
        self.logger.debug(f"[ DB ] db({self.db_name}) connection closed.")
        self.engine.dispose()
