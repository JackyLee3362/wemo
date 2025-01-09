import logging
import shutil
from pathlib import Path
from typing import Optional


from wemo.backend.common.model import MomentMsg, Thumb, Url
from wemo.backend.update.updater import Updater
from wemo.backend.utils.utils import find_img_thumb_by_url
from wemo.backend.utils.helper import get_img_from_server


logger = logging.getLogger(__name__)


class ImageUpdater(Updater):
    def __init__(self, dst_dir: Path, src_dir: Path):
        super().__init__(src_dir=src_dir, dst_dir=dst_dir)

    def update_by_moment(self, moment: MomentMsg, suffix: str = "") -> None:
        """根据 moment 更新朋友圈信息
        ~/year-month/img-url/content-length.jpg
        """
        # 获取 media 列表中
        for key, res_list in moment.update_pic.items():
            logger.info(f"[ IMG UPDATER ] updating {key}")
            # 检查是否存在
            for img in res_list:
                try:
                    url_info = img.url if key == "img" else img.thumb
                    thm_info = img.thumb
                    y_m = moment.year_month
                    urn = url_info.urn
                    dst_img_ym_dir = self.dst_dir.joinpath(y_m)
                    src_img_ym_dir = self.src_dir.joinpath(y_m)
                    dst_img_ym_urn_dir = dst_img_ym_dir.joinpath(urn)
                    res, _ = find_img_thumb_by_url(dst_img_ym_dir, urn)
                    # 如果存在，则不处理
                    if res:
                        logger.debug(
                            f"[ IMG UPDATER ] Dir({y_m})/File({res.name}) exists, skip."
                        )
                        continue
                    dst_img_ym_dir.mkdir(parents=True, exist_ok=True)
                    dst_img_ym_urn_dir.mkdir(parents=True, exist_ok=True)
                    self.handle_img_thumb(
                        src_img_ym_dir, dst_img_ym_urn_dir, url_info, thm_info
                    )
                except FileNotFoundError as e:
                    # link 不记录
                    if key == "link":
                        continue
                    msg = e.args[0] if len(e.args) > 0 else ""
                    logger.warning(
                        f"[ IMG UPDATER ] {moment.time} {suffix}-{msg}\n{moment.desc_brief}"
                    )
                except Exception as e:
                    logger.exception(e)

    def handle_img_thumb(self, src_dir: Path, dst_dir: Path, url: Url, thm: Thumb):
        # 检查是否存在
        jpg_prefix = b"\xff\xd8"
        img_content = get_img_from_server(url.url, url.params)
        thm_content = get_img_from_server(thm.url, thm.params)

        if img_content is None:
            img_content = thm_content
        if thm_content is None:
            logger.warning("[ IMG UPDATER ] can't get img or thumb from server.")
            return

        img_file_name = f"{len(img_content)}_{len(thm_content)}.jpg"
        thm_file_name = f"{len(img_content)}_{len(thm_content)}_t.jpg"

        # 如果图片已经加密，则返回图片名
        if img_content[:2] == jpg_prefix:
            # 处理图片
            dst_img_path = dst_dir.joinpath(img_file_name)
            logger.debug(
                f"[ IMG UPDATER ] Save image from server to Dir({src_dir})/File({img_file_name})."
            )
            with open(dst_img_path, "wb") as f:
                f.write(img_content)
            return
        if thm_content[:2] == jpg_prefix:
            # 处理图片
            dst_thm_path = dst_dir.joinpath(thm_file_name)
            logger.debug(
                f"[ IMG UPDATER ] Save thumb from server to Dir({src_dir.name})/File({thm_file_name})."
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
            raise FileNotFoundError(
                f"Dir({src_dir.name})/File({file_name}) not find in cache."
            )
        logger.debug(f"[ IMG UPDATER ] Dir({src_dir.name})/File({file_name}) saved.")
        shutil.copy(src_path, dst_path)

    def get_finder_images(self, msg: MomentMsg) -> Optional[str]:
        """获取视频号的封面图"""
        media = msg.finders
        for media_item in media:
            thumb_path = self.save_server_img(media_item.thumbUrn, {}, "thumb")
            return thumb_path

    def save_server_img(self, urn: str, params: dict, img_type: str):
        logger.debug("[ IMG UPDATER ]")
        img_type_lower = img_type.lower()
        if img_type_lower not in ("image", "thumb"):
            logger.warning("[ IMG UPDATER ] type is not img.")
            return
        content = get_img_from_server(urn, params)
        if content:
            tmp_p = Path(self.dst_dir).joinpath(urn)
            logger.debug(f"[ IMG UPDATER ] save a img, {urn}.")
            with open(tmp_p, "wb") as f:
                f.write(content)
