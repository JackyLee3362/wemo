import logging
import shutil
from pathlib import Path
from typing import Tuple, Optional, override


from wemo.model.moment import MomentMsg, Thumb, Url
from wemo.update.updater import Updater
from wemo.utils.utils import find_img_thumb_by_url, singleton
from wemo.utils.helper import get_img_from_server


@singleton
class ImageUpdater(Updater):
    def __init__(self, dst_dir: Path, src_dir: Path, logger: logging.Logger = None):
        super().__init__(src_dir=src_dir, dst_dir=dst_dir, logger=logger)

    @override
    def update_by_moment(self, moment: MomentMsg) -> None:
        """根据 moment 更新朋友圈信息
        ~/year-month/img-url/content-length.jpg
        """
        # 获取 media 列表中
        try:
            for img in moment.update_pic:
                # 检查是否存在
                url_info = img.url
                thm_info = img.thumb
                y_m = moment.year_month
                urn = url_info.text.split("/")[-2]
                dst_img_ym_dir = self.dst_dir.joinpath(y_m)
                src_img_ym_dir = self.src_dir.joinpath(y_m)
                dst_img_ym_urn_dir = dst_img_ym_dir.joinpath(urn)
                res, _ = find_img_thumb_by_url(dst_img_ym_dir, urn)
                # 如果存在，则不处理
                if res:
                    self.logger.debug(
                        f"[ IMG UPDATER ] Dir({y_m})/urn/File({res.name}) exists, skip."
                    )
                    continue
                dst_img_ym_dir.mkdir(parents=True, exist_ok=True)
                dst_img_ym_urn_dir.mkdir(parents=True, exist_ok=True)
                self.handle_img_thumb(
                    src_img_ym_dir, dst_img_ym_urn_dir, url_info, thm_info
                )
        except Exception as e:
            self.logger.exception(e)

    def handle_img_thumb(self, src_dir: Path, dst_dir: Path, url: Url, thm: Thumb):
        # 检查是否存在
        jpg_prefix = b"\xff\xd8"
        img_content = get_img_from_server(url.url, url.params)
        thm_content = get_img_from_server(thm.url, thm.params)

        if img_content is None:
            img_content = thm_content
        if thm_content is None:
            self.logger.warning("[ IMG UPDATER ] can't get img or thumb from server.")
            return

        img_file_name = f"{len(img_content)}_{len(thm_content)}.jpg"
        thm_file_name = f"{len(img_content)}_{len(thm_content)}_t.jpg"

        # 如果图片已经加密，则返回图片名
        if img_content[:2] == jpg_prefix:
            # 处理图片
            dst_img_path = dst_dir.joinpath(img_file_name)
            self.logger.debug(
                f"[ IMG UPDATER ] Save image from server to Dir({src_dir})/urn/File({img_file_name})."
            )
            with open(dst_img_path, "wb") as f:
                f.write(img_content)
            return
        if thm_content[:2] == jpg_prefix:
            # 处理图片
            dst_thm_path = dst_dir.joinpath(thm_file_name)
            self.logger.debug(
                f"[ IMG UPDATER ] Save thumb from server to Dir({src_dir.name})/urn/File({thm_file_name})."
            )
            with open(dst_thm_path, "wb") as f:
                f.write(thm_content)
            return
        # 如果图片已加密，进入缓存图片中匹配
        self.update_from_cache(src_dir, dst_dir, img_file_name)
        self.update_from_cache(src_dir, dst_dir, thm_file_name)
        return

    def update_from_cache(self, src_dir: Path, dst_dir: Path, file_name: str):
        # 从缓存里找文件
        src_path = src_dir.joinpath(file_name)
        dst_path = dst_dir.joinpath(file_name)
        if dst_path.exists():
            return

        # 如果没找到，日志报错
        if not src_path.exists():
            self.logger.warning(
                f"[ IMG UPDATER ] Dir({src_dir.name})/File({file_name}) not find in cache."
            )
            return
        self.logger.debug(
            f"[ IMG UPDATER ] Dir({src_dir.name})/urn/File({file_name}) saved."
        )
        shutil.copy(src_path, dst_path)

    def get_finder_images(self, msg: MomentMsg) -> Optional[str]:
        """获取视频号的封面图"""
        media = msg.finder
        for media_item in media:
            thumb_path = self.save_server_img(media_item.thumbUrn, {}, "thumb")
            return thumb_path

    def save_server_img(self, urn: str, params: dict, img_type: str):
        self.logger.debug("[ IMG UPDATER ]")
        img_type_lower = img_type.lower()
        if img_type_lower not in ("image", "thumb"):
            self.logger.warning("[ IMG UPDATER ] type is not img.")
            return
        content = get_img_from_server(urn, params)
        if content:
            tmp_p = Path(self.dst_dir).joinpath(urn)
            self.logger.debug(f"[ IMG UPDATER ] save a img, {urn}.")
            with open(tmp_p, "wb") as f:
                f.write(content)
