def xor_decode(magic: int, buf: bytes):
    if magic is None:
        raise ValueError("magic cannot be None")
    return bytearray([b ^ magic for b in list(buf)])


def guess_image_encoding_magic(buf: bytes):
    header_code, check_code = 0xFF, 0xD8
    # 微信图片加密方法对字节逐一“异或”，即 源文件^magic(未知数)=加密后文件
    # 已知jpg的头字节是0xff，将0xff与加密文件的头字节做异或运算求解magic码
    magic = header_code ^ list(buf)[0] if buf else 0x00
    # 尝试使用magic码解密，如果第二字节符合jpg特质，则图片解密成功
    _, code = xor_decode(magic, buf[:2])
    if check_code == code:
        return magic
