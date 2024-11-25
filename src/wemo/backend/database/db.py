from __future__ import annotations

from logging import Logger, getLogger

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from sqlalchemy.schema import MetaData


class UserTable(DeclarativeBase):
    @staticmethod
    def mock(seed: int) -> UserTable:
        raise NotImplementedError()

    @staticmethod
    def split_data(d1: list, d2: list):
        """
        将数据分为 update 和 insert
        d1 和 d2 里的数据都实现了 eq 和 hash
        根据 d1 和 d2 生成字典 dict1, dict2
        1. 需要更新的数据，hash 相同，eq 不同
        2. 需要插入的数据，dict2 中有，dict1 中没有
        """

        dict1 = {hash(item): item for item in d1}
        dict2 = {hash(item): item for item in d2}
        to_insert = []
        to_update = []
        for key, value in dict2.items():
            if key not in dict1:
                to_insert.append(value)
            elif key in dict1 and dict1[key] != value:
                to_update.append(value)

        return to_insert, to_update


class AbsUserDB:

    def __init__(self, db_url: str, db_name: str = None, logger: Logger = None):
        self.db_name = db_name or self.__class__.__name__
        self.db_url = db_url
        self.logger = logger or getLogger(self.db_name)

        self.table_cls_list: list[type[UserTable]] = []
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
        self.logger.debug(f"[ DB ] db({self.db_name}) init.")
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
        self.logger.debug(f"[ DB ] db({self.db_name}) is connected.")
        url = f"sqlite:///{self.db_url}"
        self.engine = create_engine(url, echo=False)

    def build_session(self):
        self.logger.debug(f"[ DB ] db({self.db_name}) session is build.")
        self.db_session = sessionmaker(bind=self.engine)
        self.session = self.db_session()

    def register_tables(self, table_cls_list: list) -> None:
        self.table_cls_list.extend(table_cls_list)

    def query_all(self, table_cls: type[UserTable]):
        data = self.session.query(table_cls).all()
        self.logger.debug(
            f"[ DB ] db({self.db_name}).table({table_cls.__name__}) query all and count({len(data)})."
        )
        return data

    def count_all(self, table_cls: type[UserTable]) -> int:
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

    def merge_all(
        self,
        tbl: type[UserTable],
        db_data: list[UserTable],
        cache_data: list[UserTable],
    ) -> None:
        if len(cache_data) <= 0:
            return
        tname = tbl.__name__
        self.count_all(tbl)
        self.logger.debug(f"[ DB ] db({self.db_name}).Table({tname}) merging...")
        to_insert, to_update = tbl.split_data(db_data, cache_data)

        self.logger.debug(f"[ DB ] Table({tname}) inserting len({len(to_insert)})...")
        if len(to_insert) > 0:
            for item in to_insert:
                self.session.merge(item)

        self.logger.debug(f"[ DB ] Table({tname}) updating len({len(to_update)})...")
        if len(to_update) > 0:
            for item in to_update:
                self.session.merge(item)

        self.session.commit()
        # with self.engine.connect() as connection:
        #     connection.execute(text("PRAGMA wal_checkpoint(FULL)"))

    def close_session(self) -> None:
        self.logger.debug(f"[ DB ] db({self.db_name}) session closed.")
        self.session.close()

    def close_connection(self) -> None:
        self.logger.debug(f"[ DB ] db({self.db_name}) connection closed.")
        self.engine.dispose()


class AbsUserCache(AbsUserDB):
    def __init__(self, db_url, db_name=None, logger=None):
        super().__init__(db_url, db_name, logger)

    def count_all(self, table_cls):
        self.init()
        res = super().count_all(table_cls)
        self.close_session()
        self.close_connection()
        return res

    def query_all(self, table_cls):
        self.init()
        res = super().query_all(table_cls)
        self.close_session()
        self.close_connection()
        return res
