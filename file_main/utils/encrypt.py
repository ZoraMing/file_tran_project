import hashlib

from django.conf import settings


def md5(data_string):
    """
    对字符串进行md5加密
    :param data_string: 字符串
    :return: 加密后的字符串
    """
    obj = hashlib.md5(settings.SECRET_KEY.encode("utf-8"))
    obj.update(data_string.encode("utf-8"))
    return obj.hexdigest()


def file_hash(file_path):
    """
    计算文件hash值
    :param file_path: 文件路径
    :return: 哈希值
    """
    sha256 = hashlib.sha256()  # 创建 SHA-256 哈希对象

    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(8192)  # 逐块读取文件
            if not chunk:
                break
            sha256.update(chunk)  # 更新哈希对象

    return sha256.hexdigest()  # 返回文件的 SHA-256 哈希值（十六进制表示）


if __name__ == "__main__":
    file_path = "media/user1/img/page-lifecycle.2e646c86.png"
    print(file_hash(file_path))