import io
import logging
from pathlib import Path

from PIL import Image

from wemo.database.misc import Misc
from wemo.utils.utils import singleton


@singleton
class AvatarUpdater:
    def __init__(self, user_avatar_dir: Path, logger: logging.Logger = None):
        self.user_avatar_dir = user_avatar_dir
        self.db = Misc()
        self.logger = logger or logging.getLogger(__name__)

    def get_avatar_by_username(self, user_name: str):
        avatar_path = self.user_avatar_dir.joinpath(f"{user_name}.png")
        if avatar_path.exists():
            return avatar_path
        blob_data = self.db.get_avatar_buffer(user_name)
        if blob_data:
            image = Image.open(io.BytesIO(blob_data.smallHeadBuf))
            image.save(avatar_path, "PNG")
            return avatar_path
        self.logger.warning(
            f"[ AVATAR UPDATER ] can't get {user_name} avatar, use default."
        )
        return self.user_avatar_dir.joinpath("default.png")
