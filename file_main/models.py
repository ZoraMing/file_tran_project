import os

from django.db import models
from django.conf import settings

from .utils.encrypt import file_hash


class User(models.Model):
    """
    用户信息表
    username: 用户名
    password: 密码
    email: 邮箱
    avatar: 头像
    temp_login: 临时登录
    temp_pwd: 临时密码
    """

    username = models.CharField(verbose_name="用户名", max_length=20, unique=True)
    password = models.CharField(verbose_name="密码", max_length=32)
    email = models.EmailField(verbose_name="邮箱", max_length=50, unique=True)
    avatar = models.ImageField(
        verbose_name="头像", upload_to="avatars/", null=True, blank=True
    )
    temp_login = models.BooleanField(verbose_name="临时登录", default=False)
    temp_pwd = models.CharField(
        verbose_name="临时密码", max_length=32, default="123456"
    )

    def save(self, *args, **kwargs):
        # 如果头像有变化，删除旧头像
        if self.pk:
            try:
                old_avatar = User.objects.get(pk=self.pk).avatar
                if old_avatar and old_avatar != self.avatar:
                    old_avatar.delete(save=False)
            except User.DoesNotExist:
                pass

        # 保存当前对象
        super().save(*args, **kwargs)

        # 处理头像命名
        if self.avatar:
            self.avatar.name = f"avatars/{self.username}.jpg"
            super().save(*args, **kwargs)


class File(models.Model):
    """
    保存文件信息的表
    file_type: img 图片 media 音视频 text 文档 other 其他
    introdece: 文件的描述
    file_name: 文件的名字
    file_suffix: 文件的后缀名
    file_path: 文件的文件夹路径
    full_file_path: 文件的完整路径
    file_size: 单位为kB
    file_hash: 文件的hash值
    upload_time: 上传时间
    user: 上传的用户id

    """

    file_types_choices = {
        "img": "图片",
        "media": "音视频",
        "txt": "文档",
        "other": "其他",
    }

    file_type = models.CharField(
        verbose_name="文件类型",
        max_length=10,
        choices=file_types_choices,
        default="other",
    )
    introduce = models.TextField(verbose_name="文件介绍",default="")
    file_name = models.CharField(verbose_name="文件名", max_length=255, default="")
    upload_time = models.DateTimeField(verbose_name="上传时间", auto_now_add=True)
    user = models.ForeignKey(
        verbose_name="上传用户", to=User, to_field="id", on_delete=models.CASCADE
    )

    file_suffix = models.CharField(verbose_name="文件后缀", max_length=20,default="")
    file_path = models.CharField(
        verbose_name="文件文件夹路径", max_length=255, default=""
    )
    full_file_path = models.CharField(
        verbose_name="文件完整路径", max_length=255, default=""
    )
    file_size = models.IntegerField(verbose_name="文件大小(KB)",default=0)
    file_hash = models.CharField(verbose_name="文件hash", max_length=255,default="sha256")

    # def save(self,fileName, *args, **kwargs):

    #     if self.pk:

    #         dir_path = os.path.join(settings.MEDIA_ROOT,self.user.username, self.file_type)
    #         file_name, file_suffix = os.path.splitext(fileName)

    #         self.file_name = file_name
    #         self.file_suffix = file_suffix
    #         self.full_file_path = dir_path
    #         self.file_size = os.path.getsize(self.full_file_path)
    #         self.file_hash = file_hash(self.full_file_path)

    #     super.save(self,*args, **kwargs)
