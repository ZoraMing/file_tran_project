from django.urls import path
from file_main.views import index, login

urlpatterns = [
    path("", index.index, name="index"),
    path("upload/", index.upload, name="upload"),
    path("download/<str:pk>/", index.download, name="download"),
    path("delete/<str:pk>/", index.delete, name="delete"),
    path("addUser/", index.addUser, name="addUser"),
    path("login/", login.login, name="login"),
    path("img_code/", login.image_code, name="img_code"),
    path("logOut/", login.logOut, name="logOut"),
    path("register/", login.register, name="register"),
]
