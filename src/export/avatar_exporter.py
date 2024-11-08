import io

from PIL import Image

from common import RC
from common.logger import LOG
from db.misc import Misc
from utils.wrapper import singleton


@singleton
class AvatarExporter:
    def __init__(self):
        self.user_avatar_dir = RC.USER_AVATAR_DIR
        self.db = Misc()

    def get_avatar_by_username(self, userName: str):
        avatar_path = self.user_avatar_dir.joinpath(f"{userName}.png")
        if avatar_path.exists():
            return avatar_path
        blob_data = self.db.get_avatar_buffer(userName)
        if blob_data:
            image = Image.open(io.BytesIO(blob_data.smallHeadBuf))
            image.save(avatar_path, "PNG")
            return avatar_path
        LOG.error(f"{userName}: 获取头像失败，使用默认头像")
        return
