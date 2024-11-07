from decrypter.image_decrypt import ImageDecrypter
from datetime import date


def test_image_decrypt():
    ImageDecrypter().decrypt_images(date(2024, 9, 1), date(2024, 11, 1))
