from utils import singleton

from .userdb import UserDB

# 聊天信息
MSG = "MSG.db"
MSGS = [f"MSG{i}.db" for i in range(0, 50)]


@singleton
class Msg(UserDB):
    def __init__(self, db_name):
        super().__init__(db_name)
