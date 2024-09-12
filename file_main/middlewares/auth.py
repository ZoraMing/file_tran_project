from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse, redirect


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """
        1.判断用户是否登录
        2.如果用户登录，继续执行视图函数
        3.如果用户未登录，跳转到登录页面
        """
        
        # print("AuthMiddleware process_request",request.path_info)
        if request.path_info in ['/login/','logout/','/image/code/']:
            
            return None

        info_dict = request.session.get("info")
        if info_dict:
            # print(info_dict)
            return None

        return redirect("/login/")


class M1(MiddlewareMixin):
    def process_request(self, request):
        # 没有返回值就是none,继续往下走
        # 有返回值,进入返回render或者函数
        # print("M1 process_request")
        pass
    def process_response(self, request, response):
        # print("M1 process_response")
        return response

