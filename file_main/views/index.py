import datetime
import os

from django.shortcuts import render,redirect
from django.http import FileResponse, HttpResponse, HttpResponseNotFound, JsonResponse

from django import forms
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
from file_main.utils.bootstarp import BootStrapModelForm, BootStrapForm
from file_main.utils.encrypt import md5, file_hash
from file_main.models import User, File
from file_main.utils.get_file import get_file_path


class UpLoadForm(BootStrapForm):

    fileType = forms.ChoiceField(label="文件类型", choices=File.file_types_choices)
    introduce = forms.CharField(label="介绍", widget=forms.Textarea)
    fileLoad = forms.FileField(label="文件")

    fields = ["file_type", "introduce", "fileLoad"]

# a = [
#         (
#         "user5\\img\\DSC05498.JPG",
#         "DSC05498",
#         "img",
#         5152,
#         "山东人过犹不及你看\r\n现成GV会比较",
#         datetime.datetime(
#             2024, 9, 12, 12, 34, 22, 572569, tzinfo=datetime.timezone.utc
#         ),
#         6,
#     ),
# ]

def index(request):
    try:
        # user_id = request.session.get("info")["id"]
        print(request.session.get("info"))
        user_now = User.objects.get(id=request.session.get("info")["id"])
    except:
        return redirect("login")

    file_list = list(File.objects.filter(user_id=user_now.id).values_list(
        "full_file_path","file_name", "file_type", "file_size", "introduce", "upload_time","id"
    ))
    # print(file_list)
    # print("-"*20)

    user_now_file_path = get_file_path(
        request.session.get("info")["name"], settings.MEDIA_ROOT
    )

    # print(user_now_file_path)

    form = UpLoadForm()
    res = {"user_now": user_now, "user_now_file_list": file_list, "form": form}

    # response = render(request, "index.html", res)
    # response['Connection'] = 'keep-alive'
    # response['Keep-Alive'] = 'timeout=300,max=1000'
    # return response
    return render(request, "index.html", res)


@csrf_exempt
def upload(request):
    if request.method == "GET":
        return HttpResponse("upload")

    user_now = User.objects.get(id=request.session.get("info")["id"])
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
        fullFilePath = os.path.join(filePath, fileName + fileSuffix)
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
            upload_time=datetime.datetime.now(),
            user_id=user_now.id,
            file_hash=fileHash,
        )
        file_instance.save()

        return JsonResponse(
            {"status": True, "msg": "上传成功"}
        )  # Replace 'success_url' with your success URL

    errors = {field: error_list for field, error_list in form.errors.items()}
    return JsonResponse({"status": False, "errors": errors})

from urllib.parse import quote

def download(request, pk):
    user_now = User.objects.get(id=request.session.get("info")["id"])
    download_file = File.objects.get(id=pk)

    if not download_file:
        return HttpResponseNotFound("File not found", status=404) 
    if not user_now.temp_login and download_file.user.id == user_now.id:
        try:
            file_path = os.path.join(
                settings.MEDIA_ROOT, download_file.full_file_path
            )
            # print(download_file)
            encoded_filename = quote(
                f"{download_file.file_name}{download_file.file_suffix}",
                safe="~@#$&()*!+=:;,.?/'",
            )

            with open(file_path, "rb") as file:
                response = HttpResponse(file.read())
                response['Content-Type']='application/octet-stream'  
                # response["Content-Disposition"] = (
                #     f'attachment; filename="{download_file.file_name}{download_file.file_suffix}"'
                # )
                response["Content-Disposition"] = (
                    f'attachment; filename*=UTF-8\'\'' 
                    f'{encoded_filename}'
                )
                return response
        except FileNotFoundError:
            return HttpResponseNotFound("File not found")
        except Exception as e:
            print(e)
            return HttpResponse(f"下载 {download_file.file_name} 失败", status=500)
    else:
        return HttpResponse("Forbidden")


def delete(request, pk):
    user_now = User.objects.get(id=request.session.get("info")["id"])
    try:
        download_file = File.objects.get(id=pk)
    except:
        return HttpResponseNotFound("File not found",stutus=404)

    if not user_now.temp_login and download_file.user.id == user_now.id:
        try:
            if download_file:
                file_path = os.path.join(
                    settings.MEDIA_ROOT, download_file.full_file_path
                )
                # print(file_path)
                download_file.delete()
                os.remove(file_path)
            return redirect("/")
        except FileNotFoundError:
            return HttpResponseNotFound("File not found", status=404)
    else:
        return HttpResponse("Forbidden", status=403)
