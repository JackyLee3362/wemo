import io
import logging
from pathlib import Path
from typing import override

from PIL import Image

from wemo.database.db_service import DBService
from wemo.update.updater import Updater
from wemo.utils.utils import singleton


@singleton
class AvatarUpdater(Updater):
    def __init__(self, db: DBService, dst_dir: Path, logger: logging.Logger = None):
        super().__init__(None, dst_dir, logger)
        self.db = db

    @override
    def update_by_username(self, username: str):
        avatar_path = self.dst_dir.joinpath(f"{username}.png")
        if avatar_path.exists():
            return avatar_path
        blob_data = self.db.get_avatar_buf_by_username(username)
        if blob_data:
            image = Image.open(io.BytesIO(blob_data.buf))
            image.save(avatar_path, "PNG")
            return avatar_path
        self.logger.warning(
            f"[ AVATAR UPDATER ] can't get {username} avatar, use default."
        )
        return self.dst_dir.joinpath("default.png")
