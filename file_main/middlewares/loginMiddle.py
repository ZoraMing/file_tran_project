# 用于监控登录功能的中间件

from django.shortcuts import redirect
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class LoginMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """
        1.判断用户是否登录
        2.如果用户登录，继续执行视图函数
        3.如果用户未登录，跳转到登录页面
        """

        safe_urls = ["/login/", "logout/", "/image/code/","/"]
        # print("AuthMiddleware process_request",request.path_info)
        if request.path_info in safe_urls:
            return None

        info_dict = request.session.get("info")
        if info_dict:
            # print(info_dict)
            return None

        return redirect('/login/')
