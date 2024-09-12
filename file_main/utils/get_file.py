import os
# from django.conf import settings


def get_file_path(user_path,MEDIA_ROOT):
    """
    获取当前用户的文件路径
    :param user_path: 用户名
    :return: 文件相对user路径列表
    """
    current_dir = os.path.join(MEDIA_ROOT,user_path)
    path_list = []
    # print(current_dir)
    try:
        for root, dirs, files in os.walk(current_dir):
            for file in files:
                path_list.append(os.path.join(root.replace(MEDIA_ROOT,""), file))
    except Exception as e:

        print(e)

    return path_list

if __name__ == "__main__":

    user_path = "user1"
    MEDIA_ROOT = "D:\\Project\\FormVS\\web\\file_ex\\file_tran\\media"

    print(get_file_path(user_path,MEDIA_ROOT))


