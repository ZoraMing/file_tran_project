from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import render,redirect
from django import forms

from file_main.utils.bootstarp import BootStrapForm,BootStrapModelForm
from file_main.models import User
from file_main.utils.img_code import check_code
from file_main.utils.encrypt import md5


class LoginForm(BootStrapForm):

    username = forms.CharField(label="用户名", widget=forms.TextInput)
    password = forms.CharField(label="密码", widget=forms.PasswordInput(render_value=True))
    code = forms.CharField(label="验证码,不区分大小写", widget=forms.TextInput)

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)


class RegisterForm(BootStrapModelForm):

    confirm_password = forms.CharField(
        label="确认密码", widget=forms.PasswordInput(render_value=True)
    )
    code = forms.CharField(label="验证码", widget=forms.TextInput)

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "confirm_password",
            "email",
            "avatar",
            "temp_pwd",
        ]
        widgets = {"password": forms.PasswordInput(render_value=True)}

    def clean_username(self):
        username = self.cleaned_data.get("username")
        user = User.objects.filter(username=username).first()
        if user:
            raise forms.ValidationError("用户名已存在")
        return username

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("password")
        confirm = md5(self.cleaned_data.get("confirm_password"))
        if confirm != pwd:
            raise forms.ValidationError("两次密码不一致")
        return confirm


class UserRegistrationForm(BootStrapModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="确认密码")

    class Meta:
        model = User
        fields = ["username", "password", "email", "avatar"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("密码和确认密码不匹配")


def login(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, "login.html", {"form": form})

    form = LoginForm(data=request.POST)
    if form.is_valid():
        # print(form.cleaned_data)

        # 校验验证码
        # if form.cleaned_data.pop("code").upper() != request.session.get("image_code","").upper():
        #     form.add_error("code", "验证码错误")
        #     return render(request, "login.html", {"form": form})

        print(form.cleaned_data)
        
        user_now = User.objects.filter(
            username=form.cleaned_data["username"],
        ).first()
        print(user_now.password)
        if user_now.password == md5(form.cleaned_data["password"]):
            form.add_error("password", "用户名或密码错误")
            return render(request, "login.html", {"form": form})

        request.session["info"] = {"id": user_now.id, "name": user_now.username}

        # 设置session过期时间回七天
        request.session.set_expiry(60 * 60 * 24 * 7)
        return redirect("/")

    return render(request, "login.html", {"form": form})


def logOut(request):
    request.session.clear()

    return redirect("/")


def register(request):

    form = RegisterForm()
    if request.method == "GET":
        return render(request, "register.html",{"form": form})

    form = RegisterForm(data=request.POST, files=request.FILES)
    print(request.POST)
    # print(request.FILES)
    # print("-" * 20)
    # print(form.is_valid())
    if form.is_valid():
        # 校验验证码
        print("post"+"-" * 20)
        print(form.cleaned_data)
        # if form.cleaned_data.pop("code").upper() != request.session.get("image_code","").upper():
        #     form.add_error("code", forms.ValidationError("验证码错误"))
        #     print(form.errors)

        #     return render(request, "register.html", {"form": form})

        # print("保存文件" + "-" * 20)
        # 保存文件
        # print(form.cleaned_data["avatar"])
        avatar = form.cleaned_data["avatar"]
        avatarSaveName =  form.cleaned_data["username"] + os.path.splitext(avatar.name)[-1]
        avatarPath = os.path.join(settings.MEDIA_ROOT, "avatars", avatarSaveName)
        with open(avatarPath, "wb+") as f:
            for chunk in avatar:
                f.write(chunk)

        userDir = os.path.join(settings.MEDIA_ROOT, form.cleaned_data["username"])
        os.mkdir(userDir, "img")
        os.mkdir(userDir, "media")
        os.mkdir(userDir, "txt")
        os.mkdir(userDir, "other")

        print("保存数据库" + "-" * 20)
        form.save()

        return HttpResponse("ok")

    print(form.errors)

    return render(request, "register.html", {"form": form})


def _register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            # user.password(user.password)  # 保存加密密码
            user.save()
            # messages.success(request, "注册成功！")
            print("注册成功")
            return redirect("login")  # 注册成功后重定向到登录页面
    else:
        form = UserRegistrationForm()

    return render(request, "register.html", {"form": form})


from django.conf import settings
import os
def image_code(request):
    font_file = os.path.join(
        settings.BASE_DIR, "file_main", "static", "font", "kumo.ttf"
    )
    # print(font_file)
    # 使用编写的check_code函数生成验证码
    img, code = check_code(font_file=font_file)
    # 将验证码保存到session中
    request.session["image_code"] = code
    # 设置验证码60秒过期
    request.session.set_expiry(60)
    # 将图片返回前端
    stream = BytesIO()
    img.save(stream, "png")

    return HttpResponse(stream.getvalue())
