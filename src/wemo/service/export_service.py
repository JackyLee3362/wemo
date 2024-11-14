from datetime import datetime
from wemo.database.micro_msg import MicroMsg
from wemo.database.sns import FeedsV20, Sns
from wemo.export.feed_exporter import MarkdownExporter
from wemo.model.dto import MomentMsg
from wemo.model.user import User


class ExportService:

    def __init__(self, user: User):
        self.user = user
        self.sns = Sns()
        self.micro_msg = MicroMsg()
        self.feed_exporter = MarkdownExporter(self.user)

    def select(
        self, begin_date: datetime, end_date: datetime, wx_ids: list[str] = None
    ):
        b_int = int(begin_date.timestamp())
        e_int = int(end_date.timestamp())
        feeds = self.sns.get_feeds_by_duration_and_wxid(b_int, e_int, wx_ids)
        return feeds

    def export(self, feeds: list[FeedsV20] = None):
        for feed in feeds:
            contact, _ = self.micro_msg.get_contact_and_labels_by_username(feed.UserName)
            moment = MomentMsg.parse_xml(feed.Content)
            self.feed_exporter.export_moment(contact, moment)
