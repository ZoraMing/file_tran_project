from django.urls import path
from file_main.views import index, login

urlpatterns = [
    path("", index.index, name="index"),
    path("upload/", index.upload, name="upload"),
    path("download/<str:pk>/", index.download, name="download"),
    path("delete/<str:pk>/", index.delete, name="delete"),
    # 用户管理
    path("login/", login.login, name="login"),
    path("img_code/", login.image_code, name="img_code"),
    path("logout/", login.logOut, name="logout"),
    path("register/", login.register, name="register"),
    path("remove_user/", login.remove_user, name="remove_user"),
]
