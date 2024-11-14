import logging
from wemo.database.micro_msg import Contact
from wemo.export.feed_exporter import MarkdownExporter
from wemo.model.moment import  MomentMsg
from wemo.model.user import User
from wemo.database.db_service import DBService


class ExportService:

    def __init__(self, user: User, db: DBService, logger: logging.Logger = None):
        self.user = user
        self.db = db
        self.logger = logger or user.logger

    def init(self):
        self.logger.info("[ EXPORT SERVICE ] init service...")
        self.feed_exporter = MarkdownExporter(self.user)

    def export(self, begin, end, wx_ids: list[str]):
        feeds = self.db.get_feeds_by_dur_ids(begin, end, wx_ids)
        for feed in feeds:
            contact = self.db.get_feeds_by_dur_ids
            self._export_moment()
            
            # self._export_moment(contact, moment)

    def _export_moment(self, contact: Contact, moment: MomentMsg):
        self.logger.info("[ EXPORT SERVICE ] exporting...")
        self.feed_exporter.export_moment(contact, moment)
