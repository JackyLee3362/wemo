from db.date_cluster import DataBaseSet
from db.sns import Sns
from decrypter.image_decrypt import ImageDecrypter

from decrypter.video_decrypt import VideoDecrypter
from export.feed_exporter import FeedExporter
from utils.datetime_helper import to_timestamp
from common.logger import LOG
import datetime


class Application:

    def __init__(self):
        pass

    def run(self):
        begin = datetime.datetime.now() - datetime.timedelta(days=1)
        end = datetime.datetime.now()
        sns = Sns()
        feed = FeedExporter()
        dbs = DataBaseSet()
        # 刷新 DB
        dbs.run()
        # 刷新 Image 和 Video
        ImageDecrypter().decrypt_images(begin.date(), end.date())
        VideoDecrypter().decrypt_videos(begin.date(), end.date())
        # 刷新 SNS

        res = sns.get_feeds_by_duration(to_timestamp(begin), to_timestamp(end))
        print("Feed 数量是", len(res))
        err_feed = []
        for item in res:
            try:
                feedId = item.FeedId
                feed.parse_feed(feedId)
            except Exception:
                err_feed.append(feedId)
                continue
        LOG.error(f"err_feed:{err_feed}")
        pass
