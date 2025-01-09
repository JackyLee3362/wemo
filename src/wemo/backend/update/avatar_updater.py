import io
import logging
from pathlib import Path

from PIL import Image

from wemo.backend.database.db_service import DBService
from wemo.backend.update.updater import Updater

logger = logging.getLogger(__name__)


class AvatarUpdater(Updater):

    def __str__(self):
        return "[ AVATAR UPDATER ]"

    def __init__(self, db: DBService, dst_dir: Path):
        super().__init__(None, dst_dir)
        self.db = db

    def update_by_username(self, username: str):
        if username.endswith("stranger"):
            return self.dst_dir.joinpath("default.png")
        avatar_path = self.dst_dir.joinpath(f"{username}.png")

        if avatar_path.exists():
            return avatar_path
        blob_data = self.db.get_avatar_buf_by_username(username)
        if blob_data:
            image = Image.open(io.BytesIO(blob_data.buf))
            image.save(avatar_path, "PNG")
            return avatar_path
        return self.dst_dir.joinpath("default.png")
