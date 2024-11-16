from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine
from pathlib import Path

db_path = Path(__file__).parent.joinpath("test.db")


def test_1():
    engine = create_engine(f"sqlite:///{db_path}")
    engine.connect()
    meta = MetaData()
    Table(
        "students",
        meta,
        Column("id", Integer, primary_key=True),
        Column("first_name", String),
        Column("last_name", String),
    )
    meta.create_all(engine)
    # os.remove(db_path)
