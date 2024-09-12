from datetime import datetime
import os

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound,JsonResponse

from django import forms
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
from file_main.utils.bootstarp import BootStrapModelForm,BootStrapForm
from file_main.utils.encrypt import md5,file_hash
from file_main.models import User, File
from file_main.utils.get_file import get_file_path


class UserForm(BootStrapModelForm):
    class Meta:
        model = User
        fields = "__all__"


class UpLoadForm(BootStrapForm):


    fileType = forms.ChoiceField(label="文件类型", choices=File.file_types_choices)
    introduce = forms.CharField(label="介绍",widget=forms.Textarea)
    fileLoad = forms.FileField(label="文件")

    fields = ["file_type", "introduce","fileLoad"]


def index(request):

    user_now = request.session.get("info")["id"]
    # print(request.session.get("info"))
    user_now = User.objects.get(id=user_now)

    file_list = File.objects.filter(user_id=user_now.id).values_list('file_name','file_path','file_type','file_size','introduce','upload_time')
    print(file_list)
    # print("-"*20)

    user_now_file_path = get_file_path(request.session.get("info")["name"], settings.MEDIA_ROOT)

    # print(user_now_file_path)

    form = UpLoadForm()
    res = {"user_now": user_now, "user_now_file_path": user_now_file_path ,"form":form}

    return render(request, "index.html", res)


def addUser(request):
    if request.method == "POST":

        form = UserForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            # 更改保存到磁盘的文件名字
            user = form.save(commit=False)
            user.avatar.name = f"{user.username}.jpg"
            user.save()

            print(form.cleaned_data)
            return HttpResponse("ok")

        res = {
            "form": form,
        }
        return render(request, "upload.html", res)

    form = UpLoadForm()
    res = {"form": form}

    return HttpResponse(request, res)


@csrf_exempt
def upload(request):
    if request.method == "GET":
        return HttpResponse("upload")

    # user_id = 5
    user_now = User.objects.filter().first()
    # print(user_now.username)
    # print("-"*20)
    # print(request.POST)
    # print("-" * 20)

    form = UpLoadForm(request.POST, request.FILES)
    if form.is_valid():
        fileLoad = form.cleaned_data["fileLoad"]
        fileType = form.cleaned_data["fileType"]
        introduce = form.cleaned_data["introduce"]

        fileSize = int(fileLoad.size / 1024)  # kB
        fileSuffix = os.path.splitext(fileLoad.name)[-1]
        fileName = fileLoad.name.replace(fileSuffix, "")

        # 服务器保存路径
        filePath = os.path.join(user_now.username, fileType)
        fullFilePath = os.path.join(filePath,fileName+fileSuffix)
        # print(fileName)
        # print(fileSuffix)
        # print(filePath)
        # print(fullFilePath)
        savePath = os.path.join(settings.MEDIA_ROOT, fullFilePath)
        with open(savePath, "wb+") as f:
            for chunk in fileLoad.chunks():
                f.write(chunk)

        fileHash = file_hash(savePath)

        # 创建和保存 File instance
        file_instance = File(
            file_type=fileType,
            introduce=introduce,
            file_size=fileSize,
            file_name=fileName,
            file_suffix=fileSuffix,
            file_path=filePath,
            full_file_path=fullFilePath,
            upload_time=datetime.now(),
            user_id=user_now.id,
            file_hash = fileHash,
        )
        file_instance.save()

        return JsonResponse(
            {"status": True,"msg": "上传成功"}
        )  # Replace 'success_url' with your success URL

    errors = {field:error_list for field, error_list in form.errors.items()}
    return JsonResponse({"status": False, "errors": errors})

# D:\Project\FormVS\web\file_ex\file_tran\media\user1

def download(request, pk):
    try:
        user = User.objects.filter(id=pk).first()
        if user.avatar:
            file_path = user.avatar.path
            with open(file_path, "rb") as file:
                response = HttpResponse(file.read(), content_type="image/jpeg")
                response["Content-Disposition"] = (
                    f'attachment; filename="{user.user_name}.jpg"'
                )
                return response
    except User.DoesNotExist:
        return HttpResponseNotFound("User not found")
    except FileNotFoundError:
        return HttpResponseNotFound("File not found")


def delete(request, pk):
    try:
        user = User.objects.filter(id=pk)
        if user.avatar:
            user.avatar.delete()
            user.avatar = None
            user.save()
            return HttpResponse("File deleted successfully!")
    except User.DoesNotExist:
        return HttpResponseNotFound("User not found")
    return HttpResponse("No file to delete")
