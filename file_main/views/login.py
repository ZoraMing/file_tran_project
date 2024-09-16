from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import render,redirect
from django import forms

from file_main.utils.bootstarp import BootStrapForm,BootStrapModelForm
from file_main.models import User,File
from file_main.utils.img_code import check_code
from file_main.utils.encrypt import md5


class LoginForm(BootStrapForm):

    username = forms.CharField(label="用户名", widget=forms.TextInput)
    password = forms.CharField(label="密码", widget=forms.PasswordInput(render_value=True))
    code = forms.CharField(label="验证码,不区分大小写", widget=forms.TextInput)

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)

def validator_type(file):
    suffix_list = (".png", ".jpg", ".txt",".html",".doc",".zip",".gz")
    if not file.name.endwith(suffix_list):
        raise forms.ValidationError


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
        widgets = {
            "password": forms.PasswordInput(render_value=True),
            # "avatar": forms.FileField(validators=[validator_type]),
        }


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
    # def clean_avatar(self):
    #     if not self.cleaned_data.get("avatar"):
    #         print(self.cleaned_data.get("avatar"))

    #         return super().clean()
    #     else:

    #         raise forms.ValidationError("头像未上传")


def login(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, "login.html", {"form": form})

    form = LoginForm(data=request.POST)
    if form.is_valid():
        # print(form.cleaned_data)

        user_now = User.objects.filter(
            username=form.cleaned_data["username"],
        ).first()
        if user_now is None:
            form.add_error("username",f"用户: {form.cleaned_data["username"]} 不存在")
            return render(request, "login.html", {"form": form})
            
        # 校验验证码
        if form.cleaned_data.pop("code").upper() != request.session.get("image_code","").upper():
            form.add_error("code", "验证码错误")
            return render(request, "login.html", {"form": form})

        print(form.cleaned_data)
        
        print(user_now.password)
        if (md5(form.cleaned_data["password"]) == user_now.password) or (md5(form.cleaned_data["password"]) == user_now.temp_pwd):
            form.add_error("password", "用户名或密码错误")
            return render(request, "login.html", {"form": form})

        request.session["info"] = {"id": user_now.id, "name": user_now.username}

        # 设置session过期时间回七天
        request.session.set_expiry(60 * 60 * 24 * 7)
        return redirect("/")

    return render(request, "login.html", {"form": form})


def logOut(request):
    try:
        request.session.clear()
    except: pass
    return redirect("/")


def register(request):

    form = RegisterForm()
    if request.method == "GET":
        return render(request, "register.html",{"form": form})

    form = RegisterForm(data=request.POST, files=request.FILES)

    if form.is_valid():
        # 校验验证码

        if form.cleaned_data.pop("code").upper() != request.session.get("image_code","").upper():
            form.add_error("code", forms.ValidationError("验证码错误"))
            # print(form.errors)

            return render(request, "register.html", {"form": form})

        try:
            # 保存文件
            avatar = form.cleaned_data["avatar"]
            org_avatar_name = avatar.name
            avatarSaveName =  form.cleaned_data["username"] + os.path.splitext(avatar.name)[-1]
            print(os.path.splitext(avatar.name)[-1])
            
            avatarPath = os.path.join(settings.MEDIA_ROOT, "avatars", avatarSaveName)
            # print(form)

        except Exception as e:
            form.add_error("avatar",forms.ValidationError("头像未上传"))
            print(e)
            return render(request, "register.html", {"form": form})

            # 删除原始临时文件
            
        with open(avatarPath, "wb+") as f:
            for chunk in avatar:
                f.write(chunk)

        userDir = os.path.join(settings.MEDIA_ROOT, form.cleaned_data["username"])

        os.mkdir(userDir,777)
        os.mkdir(os.path.join(userDir, "img"),777)
        os.mkdir(os.path.join(userDir, "media"),777)
        os.mkdir(os.path.join(userDir, "txt"),777)
        os.mkdir(os.path.join(userDir, "other"), 777)

        # print("保存数据库" + "-" * 20)

        form.cleaned_data["avatar"].name = avatarSaveName
        form.cleaned_data["temp_pwd"] = md5(form.cleaned_data["temp_pwd"])
        print(form.cleaned_data)
        form.save()
        
        temp_file_path = os.path.join(settings.MEDIA_ROOT, "avatars", org_avatar_name)
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            

        return redirect("/login/")

    # print(form.errors)

    return render(request, "register.html", {"form": form})


def remove_user(request):

    if request.method == "POST":
        try:
            user_id = request.session.get("info")["id"]  
        except KeyError:
            
            return redirect("/login/")

        user = User.objects.filter(id=user_id).first()
        if not user:
            return redirect("/login/")

        user_file = File.objects.filter(user_id=user_id).all()

        user_dir = os.path.join(settings.MEDIA_ROOT, user.username)

        # 删除用户文件
        for f in user_file:
            f.delete()

        # 删除用户
    
        import shutil
        # 检查并删除空目录
        if os.path.exists(user_dir):
            shutil.rmtree(user_dir)

        # 获取头像路径
        avatar_path = os.path.join(settings.MEDIA_ROOT, str(user.avatar))
        print(avatar_path)
        if os.path.exists(avatar_path):
            if os.path.exists(avatar_path):
                os.remove(avatar_path)

        user.delete()
        
        request.session.clear()

        # logger.info(f"Deleted user id={user_id} successfully")
        return redirect("/login/")


    return redirect("/login/")


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
    # 设置验证码600秒过期
    request.session.set_expiry(600)
    # 将图片返回前端
    stream = BytesIO()
    img.save(stream, "png")

    return HttpResponse(stream.getvalue())
