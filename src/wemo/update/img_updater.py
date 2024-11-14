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

    @override
    def update_by_moment(self, moment: MomentMsg) -> None:
        """根据 moment 更新朋友圈信息
        ~/year-month/img-url/content-length.jpg
        """
        # 获取 media 列表中
        try:
            for img in moment.imgs:
                # 检查是否存在
                url_info = img.url
                thm_info = img.thumb
                urn = url_info.text.split("/")[-2]
                dst_img_dir = self.dst_dir.joinpath(moment.year_month)
                src_img_dir = self.src_dir.joinpath(moment.year_month)
                dst_img_urn_dir = dst_img_dir.joinpath(urn)
                res0, _ = find_img_thumb_by_url(dst_img_dir, urn)
                # 如果存在，则不处理
                if res0:
                    self.logger.debug(
                        f"[ IMG UPDATER ] file({res0.name}) exists, skip."
                    )
                    continue
                dst_img_dir.mkdir(parents=True, exist_ok=True)
                dst_img_urn_dir.mkdir(parents=True, exist_ok=True)
                self.handle_img_thumb(src_img_dir, dst_img_urn_dir, url_info, thm_info)
        except Exception as e:
            self.logger.exception(e)

    def handle_img_thumb(self, src_dir: Path, dst_dir: Path, url: Url, thm: Thumb):
        # 检查是否存在
        img_file_name, thm_file_name = self.update_from_server(url, thm, dst_dir)
        if img_file_name is None:
            self.logger.warning(
                f"[ IMG UPDATER ] request fail with img({dst_dir.stem})."
            )
            return
        # 如果图片已加密，进入缓存图片中匹配
        self.update_from_cache(src_dir, dst_dir, img_file_name)
        self.update_from_cache(src_dir, dst_dir, thm_file_name)

    def update_from_server(self, url: Url, thm: Thumb, dst_dir: Path) -> Tuple:
        # 从服务器下载
        jpg_prefix = b"\xff\xd8"
        img_content = get_img_from_server(url.url, url.params)
        thm_content = get_img_from_server(thm.url, thm.params)

        if img_content is None:
            return None, None

        img_file_name = f"{len(img_content)}_{len(thm_content)}.jpg"
        thm_file_name = f"{len(img_content)}_{len(thm_content)}_t.jpg"

        # 如果图片已经加密，则返回图片名

        if img_content[:2] != jpg_prefix:
            return img_file_name, thm_file_name

        # 处理图片
        dst_img_path = dst_dir.joinpath(img_file_name)
        dst_thm_path = dst_dir.joinpath(thm_file_name)

        self.logger.debug(
            f"[ IMG UPDATER ] save from server. Path({dst_dir.name}) save img and thumb."
        )
        with open(dst_img_path, "wb") as f:
            f.write(img_content)
        with open(dst_thm_path, "wb") as f:
            f.write(thm_content)
        return None, None

    def update_from_cache(self, src_dir: Path, dst_dir: Path, file_name: str):
        # 从缓存里找文件
        src_path = src_dir.joinpath(file_name)
        dst_path = dst_dir.joinpath(file_name)
        if dst_path.exists():
            return

        # 如果没找到，日志报错
        if not src_path.exists():
            self.logger.warning(f"[ IMG UPDATER ] from cache not find {file_name}.")
            return
        self.logger.debug(f"[ IMG UPDATER ] from cache find and save {file_name}.")
        shutil.copy(src_path, dst_path)

    def get_finder_images(self, msg: MomentMsg) -> Optional[str]:
        """获取视频号的封面图"""
        media = msg.finder
        for media_item in media:
            thumb_path = self.save_server_img(media_item.thumbUrn, {}, "thumb")
            return thumb_path
