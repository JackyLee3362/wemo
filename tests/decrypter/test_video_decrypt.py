from decrypter.video_decrypt import VideoDecrypter
from datetime import date


def test_video_decrypt():
    video_decrypter = VideoDecrypter()
    video_decrypter.decrypt_videos(date(2024, 9, 1), date(2024, 11, 1))
