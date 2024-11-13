from wemo.base.db import DbCacheSet
from wemo.database.micro_msg import MicroMsg, MicroMsgCache
from wemo.database.misc import Misc, MiscCache
from wemo.database.sns import Sns, SnsCache
from wemo.update.img_updater import ImageUpdater
from wemo.update.video_updater import VideoUpdater
from wemo.model.user import User


class UserDataUpdateService:

    def __init__(self, user: User):
        logger = user.logger
        self.logger = logger
        d1 = user.data_dir.db_dir  # 用户数据库数据
        d2 = user.cache_dir.db_dir  # 用户数据库缓存

        self.sns = DbCacheSet(
            Sns(d1.joinpath("Sns.db"), logger),
            SnsCache(d2.joinpath("Sns.db"), logger),
            logger,
        )
        self.micro_msg = DbCacheSet(
            MicroMsg(d1.joinpath("MicroMsg.db"), logger),
            MicroMsgCache(d2.joinpath("MicroMsg.db"), logger),
            logger,
        )
        self.misc = DbCacheSet(
            Misc(d1.joinpath("Misc.db"), logger),
            MiscCache(d2.joinpath("Misc.db"), logger),
            logger,
        )
        self.img_exporter = ImageUpdater(
            user_data_img_dir=user.data_dir.img_dir,
            user_cache_img_dir=user.cache_dir.img_dir,
            logger=logger,
        )
        self.video_exporter = VideoUpdater(
            user_data_video_dir=user.data_dir.video_dir,
            user_cache_video_dir=user.cache_dir.video_dir,
        )

        self.sns.init_db_cache()
        self.micro_msg.init_db_cache()
        self.misc.init_db_cache()

    def update(self):
        self._update_db(self.micro_msg)
        self._update_db(self.misc)
        self._update_db(self.sns)

    def _update_db(self, dcs: DbCacheSet):
        db_name = dcs.db.db_name
        db = dcs.db
        cache = dcs.cache
        for table_cls in dcs.db.table_cls_list:
            t_name = table_cls.__name__
            self.logger.debug(f"[ {db_name}.{t_name} ] ----- start -----")
            n1 = db.count_all(table_cls)
            cache_data = cache.query_all(table_cls)
            db.merge_all(cache_data)
            n2 = db.count_all(table_cls)
            self.logger.debug(
                f"[ {db_name}.{t_name} ] db total is {n1}, cache total is {n2}"
            )
            self.logger.debug(f"[ {db_name}.{t_name} ] -----  end  -----")

    def update_image(self):
        pass

    def update_video(self):
        pass
