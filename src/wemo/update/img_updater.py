import logging
import shutil
from pathlib import Path
from typing import Tuple, Optional

import requests

from wemo.model.dto import MomentMsg, Thumb, Url
from wemo.utils.utils import find_img_thumb_by_url, singleton


def get_image_from_wx_server(url, params: dict) -> bytes:
    """向微信服务器请求图片"""
    if params:
        query_string = "&".join(f"{key}={value}" for key, value in params.items())
        url = f"{url}?{query_string}"
    response = requests.get(url)
    if response.ok:
        return response.content


@singleton
class ImageUpdater:
    def __init__(
        self,
        user_data_img_dir: Path,
        user_cache_img_dir: Path,
        logger: logging.Logger = None,
    ):
        self.data_img_dir = user_data_img_dir
        self.cache_img_dir = user_cache_img_dir
        self.logger = logger or logging.getLogger(__name__)

    def save_server_img(self, urn: str, params: dict, img_type: str):
        self.logger.info("[ SAVE IMG ]")
        img_type_lower = img_type.lower()
        if img_type_lower not in ("image", "thumb"):
            self.logger.error("[ TYPE ERROR ] type is not img.")
            return
        content = get_image_from_wx_server(urn, params)
        if content:
            tmp_p = Path(self.data_img_dir).joinpath(urn)
            self.logger.info(f"[ SAVE SERVER IMAGE ] save a img, {urn}.")
            with open(tmp_p, "wb") as f:
                f.write(content)

    def handle_moment(self, moment: MomentMsg) -> None:
        """根据 moment 更新朋友圈信息
        ~/year-month/img-url/content-length.jpg
        """
        # 获取 media 列表中
        for img in moment.imgs:
            # 检查是否存在
            url_info = img.url
            thm_info = img.thumb
            dir_name = url_info.text.split("/")[-2]
            dst_img_dir = self.data_img_dir.joinpath(moment.year_month, dir_name)
            src_img_dir = self.cache_img_dir.joinpath(moment.year_month)
            res0, _ = find_img_thumb_by_url(dst_img_dir, dir_name)
            # 如果存在，则不处理
            if res0:
                continue
            dst_img_dir.mkdir(parents=True, exist_ok=True)
            self.handle_img_thumb(src_img_dir, dst_img_dir, url_info, thm_info)

    def handle_img_thumb(
        self, src_img_dir: Path, dst_img_dir: Path, img_info: Url, thm_info: Thumb
    ):
        # 检查是否存在
        img_file_name, thm_file_name = self.update_from_server(
            img_info, thm_info, dst_img_dir
        )
        if img_file_name is None:
            self.logger.warning(
                f"[ BAD REQUEST ] can't request img({dst_img_dir.stem}) from server."
            )
            return
        # 如果图片已加密，进入缓存图片中匹配
        self.update_from_cache(src_img_dir, dst_img_dir, img_file_name)
        self.update_from_cache(src_img_dir, dst_img_dir, thm_file_name)

    def update_from_server(
        self, url_info: Url, thm_info: Thumb, dst_dir: Path
    ) -> Tuple:
        # 从服务器下载
        jpg_prefix = b"\xff\xd8"
        img_content = get_image_from_wx_server(url_info.url, url_info.params)
        thm_content = get_image_from_wx_server(thm_info.url, thm_info.params)

        if img_content is None:
            return None, None

        img_file_name = f"{len(img_content)}_{len(thm_content)}.jpg"
        thm_file_name = f"{len(img_content)}_{len(thm_content)}_t.jpg"

        # 如果图片已经加密，则返回图片名

        if img_content[:2] == jpg_prefix:
            return img_file_name, thm_file_name

        dst_img_path = dst_dir.joinpath(img_file_name)
        dst_thm_path = dst_dir.joinpath(thm_file_name)

        self.logger.info(f"[ SAVE SERVER ] Path({dst_dir.name}) save img and thumb.")
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
            self.logger.error(f"[ NOT FIND FROM CACHE] not find {file_name}.")
            return
        self.logger.debug(f"[ FIND IMG FROM CACHE ] find {file_name}.")
        shutil.copy(src_path, dst_path)

    def get_finder_images(self, msg: MomentMsg) -> Optional[str]:
        """获取视频号的封面图"""
        media = msg.finder
        for media_item in media:
            thumb_path = self.save_server_img(media_item.thumbUrn, {}, "thumb")
            return thumb_path
