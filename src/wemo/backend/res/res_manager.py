import logging
from wemo.backend.ctx import Context
from wemo.backend.model.moment import MomentMsg
from wemo.backend.utils.utils import (
    find_img_thumb_by_url,
    find_video_by_md5_or_duration,
)


import shutil
from pathlib import Path


logger = logging.getLogger(__name__)


class ResourceManager:
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.user_dir = ctx.user_data_dir
        self.default_avatar = "default_avatar.jpg"
        self.default_img = "default_image.jpg"

    def get_imgs(self, moment: MomentMsg):
        out = self.ctx.output_date_dir
        res = []
        data_img_path = self.ctx.user_data_dir.img_dir
        for img in moment.imgs:
            # 检查是否存在
            urn_dir = img.url.urn
            year_month_dir = data_img_path.joinpath(moment.year_month)
            img_path, thm_path = find_img_thumb_by_url(year_month_dir, urn_dir)
            if img_path is not None:
                img_copy = Path(shutil.copy2(img_path, out.img_dir))
                img_relative = img_copy.relative_to(out)
            else:
                img_relative = out.img_dir.joinpath(self.default_img)

            if thm_path is not None:
                thm_copy = Path(shutil.copy2(thm_path, out.img_dir))
                thm_relative = thm_copy.relative_to(out)
            else:
                thm_relative = out.img_dir.joinpath(self.default_img)

            img.url = img_relative
            img.thumb = thm_relative

            res.append(img)
        return res

    def get_videos(self, moment: MomentMsg):
        out = self.ctx.output_date_dir
        res = []
        data_video_path = self.ctx.user_data_dir.video_dir.joinpath(moment.year_month)
        for video in moment.videos:
            video_path = find_video_by_md5_or_duration(
                data_video_path, video.url.md5, video.videoDuration
            )
            if video_path is not None:
                video_copy = Path(shutil.copy2(video_path, out.video_dir))
                video_relative = Path(video_copy).relative_to(out)
                video.url = video_relative
                res.append(video)
        return res

    def get_avatar_url(self, moment: MomentMsg):
        out = self.ctx.output_date_dir
        dst_dir = self.ctx.user_data_dir.avatar_dir
        file_name = moment.username + ".png"
        avatar_path = dst_dir.joinpath(file_name)
        if avatar_path.exists():
            avatar_copy = Path(shutil.copy2(avatar_path, out.avatar_dir))
            avatar_relative = avatar_copy.relative_to(out)
            return avatar_relative
        logger.warning("Avatar not found, using default.")
        return out.avatar_dir.joinpath(self.default_avatar)

    def get_links(self, moment: MomentMsg):
        out = self.ctx.output_date_dir
        res = []
        data_img_path = self.ctx.user_data_dir.img_dir
        for link in moment.links:
            urn_dir = link.thumb.urn
            year_month_dir = data_img_path.joinpath(moment.year_month)
            img_url, _ = find_img_thumb_by_url(year_month_dir, urn_dir)
            if img_url is not None:
                img_copy = Path(shutil.copy2(img_url, out.img_dir))
                img_relative = img_copy.relative_to(out)
                link.thumb = img_relative
                link.url = link.url.text
                res.append(link)
            else:
                link.thumb = out.img_dir.joinpath(self.default_img)
                res.append(link)
        return res

    def get_musics(self, moment: MomentMsg):
        out = self.ctx.output_date_dir
        res = []
        data_img_path = self.ctx.user_data_dir.img_dir
        for music in moment.musics:
            urn_dir = music.thumb.urn
            year_month_dir = data_img_path.joinpath(moment.year_month)
            img_url, _ = find_img_thumb_by_url(year_month_dir, urn_dir)
            if img_url is not None:
                img_copy = Path(shutil.copy2(img_url, out.img_dir))
                img_relative = img_copy.relative_to(out)
                music.thumb = img_relative
                music.url = music.url.url
                res.append(music)
            else:
                music.thumb = out.img_dir.joinpath(self.default_img)
                res.append(music)
        return res

    def get_finders(self, moment: MomentMsg):
        out = self.ctx.output_date_dir
        res = []
        data_img_path = self.ctx.user_data_dir.img_dir
        for finder in moment.finders:
            urn_dir = finder.thumb.urn
            year_month_dir = data_img_path.joinpath(moment.year_month)
            img_url, _ = find_img_thumb_by_url(year_month_dir, urn_dir)
            if img_url is not None:
                img_copy = Path(shutil.copy2(img_url, out.img_dir))
                img_relative = img_copy.relative_to(out)
                finder.thumb = img_relative
                finder.title = finder.title or ""
                finder.description = finder.description or ""
                res.append(finder)
            else:
                finder.thumb = out.img_dir.joinpath(self.default_img)
                res.append(finder)
        return res
