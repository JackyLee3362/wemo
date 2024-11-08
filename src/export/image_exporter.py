from pathlib import Path
import shutil
from typing import Tuple, Optional
from common.logger import LOG
from common.user_constant import RC
from model.moment_msg import Media, MomentMsg
import requests

from utils.wrapper import singleton


def get_image_from_wx_server(url, params: tuple) -> bytes:
    """向微信服务器请求图片"""
    LOG.debug("向微信服务器请求图片")
    idx, token = params
    # 如果需要传递token
    if idx and token:
        url = f"{url}?idx={idx}&token={token}"
    response = requests.get(url)
    if response.ok:
        return response.content


@singleton
class ImageExporter:
    def __init__(self):
        self.app_sns_images = RC.USER_SNS_IMAGE
        self.app_sns_thumbs = RC.USER_SNS_THUMB
        self.app_sns_cache_img = RC.USER_CACHE_SNS_IMAGE
        self.app_sns_cache_thumb = RC.USER_CACHE_SNS_THUMB

    def save_image(self, url: str, params: tuple, img_type: str):
        """下载图片"""
        LOG.info("下载图片")
        file_name = url.split("/")[-2]
        if not (img_type == "image" or img_type == "thumb"):
            LOG.error("图片类型参数错误")
            return
        content = get_image_from_wx_server(params)
        if content:
            tmp_p = None
            if img_type.lower() == "image":
                tmp_p = Path(self.app_sns_images).joinpath(file_name)
            elif img_type.lower() == "thumb":
                tmp_p = Path(self.app_sns_thumbs).joinpath(file_name)
            with open(tmp_p) as f:
                f.write(content)

    @staticmethod
    def get_image_thumb_and_url(media: Media, style: int) -> Tuple[Tuple, Tuple]:
        """获取图片的缩略图与大图的链接"""
        thumb_info = url_info = None
        # 普通图片
        if media.type == "2":
            thumb_info = (
                media.thumb.text,
                media.thumb.enc_idx,
                media.thumb.token,
            )
            url_info = (media.url.text, media.url.enc_idx, media.url.token)
        # 微信音乐
        if media.type == "5":
            thumb_info = (media.thumb.text, "", "")
            url_info = (media.thumb.text, "", "")
        # 超链接类型
        if style == 3:
            thumb_info = (media.thumb.text, "", "")
            url_info = (media.thumb.text, "", "")

        return thumb_info, url_info

    def handle_image_from_moment(self, msg: MomentMsg) -> list[Tuple]:
        """获取一条朋友圈的全部图像， 返回值是一个元组列表
        [(缩略图路径，原图路径)，(缩略图路径，原图路径)]
        """
        # 如果不存在 Media，直接返回
        if not msg.timelineObject.ContentObject.mediaList:
            return None

        # 获取 media 列表中
        res = []
        medias = msg.timelineObject.ContentObject.mediaList.media
        for media in medias:
            # thumb_obj = media.thumb
            url_obj = media.url
            thm_info, url_info = self.get_image_thumb_and_url(media, msg.style)
            url_name = url_obj.text.split("/")[-2]
            file_name = f"{msg.create_date}_{url_name}.jpg"
            image_path = self.app_sns_images.joinpath(file_name)
            thumb_path = self.app_sns_thumbs.joinpath(file_name)
            if image_path.exists():
                LOG.info(f"{image_path.name} 跳过")
                res.append(image_path)
                continue
            if thm_info and url_info:
                # 主图内容
                img_content = get_image_from_wx_server(url_info[0], url_info[1:])
                # 如果拿不到主图数据
                if not img_content:
                    LOG.error("获取图片失败，跳过")
                    continue
                # 如果在微信服务器获取到 jpg 图片
                if img_content[:2] == b"\xff\xd8":
                    with open(self.app_sns_images.joinpath(file_name), "wb") as f:
                        f.write(img_content)
                    # 缩略图内容
                    thm_content = get_image_from_wx_server(thm_info[0], thm_info[1:])
                    with open(self.app_sns_thumbs.joinpath(file_name), "wb") as f:
                        f.write(thm_content)
                # 如果图片已加密，进入缓存图片中匹配
                else:
                    # 获取类似 2024-06 格式的时间
                    year_month = msg.create_year_month
                    img_content = get_image_from_wx_server(url_info[0], url_info[1:])
                    thm_content = get_image_from_wx_server(thm_info[0], thm_info[1:])
                    # 从缓存里找文件
                    cache_name = f"{len(img_content)}_{len(thm_content)}.jpg"
                    cache_image_path = self.app_sns_cache_img.joinpath(
                        year_month, cache_name
                    )
                    cache_thumb_path = self.app_sns_cache_thumb.joinpath(
                        year_month, cache_name
                    )
                    if cache_image_path.exists() and not image_path.exists():
                        shutil.copy(cache_image_path, image_path)
                        res.append(image_path)
                    if cache_thumb_path.exists() and not thumb_path.exists():
                        shutil.copy(cache_thumb_path, thumb_path)

        return res

    def get_finder_images(self, msg: MomentMsg) -> Optional[str]:
        """获取视频号的封面图"""
        results = None
        if not msg.timelineObject.ContentObject.finderFeed:
            return results

        if not msg.timelineObject.ContentObject.finderFeed.mediaList:
            return results

        media = msg.timelineObject.ContentObject.finderFeed.mediaList.media
        for media_item in media:
            thumb_path = self.save_image((media_item.thumbUrl, "", ""), "thumb")
            return thumb_path
