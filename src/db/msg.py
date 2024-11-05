from utils import singleton
from .userdb import UserDB

# 聊天信息
MSG = "MSG.db"
MSGS = [f"MSG{i}.db" for i in range(0, 50)]
db_path = None  # DB_USER_DIR / MSG


@singleton
class Msg(UserDB):
    def __init__(self):
        self.init_user_db()
        super.__init__(
            MSG,
        )

    def get_contact(self, contacts):
        """这里查了一遍聊天记录，根据聊天记录最后一条按时间
        对联系人进行排序
        """
        sql = """select StrTalker, MAX(CreateTime) from MSG group by StrTalker"""
        res = self.execute_sql(sql, None)
        res = {StrTalker: CreateTime for StrTalker, CreateTime in res}
        contacts = [list(cur_contact) for cur_contact in contacts]
        for i, cur_contact in enumerate(contacts):
            if cur_contact[0] in res:
                contacts[i].append(res[cur_contact[0]])
            else:
                contacts[i].append(0)
        contacts.sort(key=lambda cur_contact: cur_contact[-1], reverse=True)
        return contacts

    def get_messages_calendar(self, username_):
        sql = """
            SELECT strftime('%Y-%m-%d',CreateTime,'unixepoch','localtime') as days
            from (
                SELECT MsgSvrID, CreateTime
                FROM MSG
                WHERE StrTalker = ?
                ORDER BY CreateTime
            )
            group by days
        """
        result = self.execute_sql(sql, [username_])
        return [date[0] for date in result]
