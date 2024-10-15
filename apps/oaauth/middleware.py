#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/15 下午4:45
@ Author      : Poco Ray
@ File        : middleware.py
@ Description : 自定义中间件, 实现JWT认证，除登录注册页面，其它页面都需要登录之后才能访问
中间件作用: 1、在请求到达视图之前, 对请求进行预处理
          2、在请求到达视图之后(浏览器之前), 对响应进行预处理
"""
from django.utils.deprecation import MiddlewareMixin
import jwt
from django.conf import settings
from rest_framework.authentication import get_authorization_header
from rest_framework import exceptions
from jwt.exceptions import ExpiredSignatureError
from django.contrib.auth import get_user_model
from django.http.response import JsonResponse
from rest_framework.status import HTTP_403_FORBIDDEN
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import reverse

OAUser = get_user_model()


class LoginCheckMiddleware(MiddlewareMixin):
    """
    自定义登录校验中间件
    1、如果返回None, 那么会正常执行(包括执行视图、其他中间件的代码)
    2、如果返回HttpResponse对象, 那么不会执行视图和后面的中间件的代码
    """
    keyword = 'JWT'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 对于那些不需要登录即可访问的视图，设置白名单
        # self.white_list = ["/auth/login", "/staff/activate"]
        self.white_list = [reverse("oaauth:login"), reverse("staff:activate")]

    def process_view(self, request, view_func, view_args, view_kwargs):
        """请求到达视图之前"""

        # 如果请求路径在白名单中，或者请求路径是media(静态资源文件)的路径, 则不需要登录即可访问
        if request.path in self.white_list or request.path.startswith(settings.MEDIA_URL):
            request.user = AnonymousUser()  # 匿名用户
            request.auth = None
            return None

        try:
            auth = get_authorization_header(request).split()

            # 如果auth为空或者auth[0]不等于JWT，抛出提示信息
            if not auth or auth[0].lower() != self.keyword.lower().encode():
                raise exceptions.ValidationError("请传入JWT token！")

            # 如果auth长度为1，返回错误信息
            if len(auth) == 1:
                msg = '不可用的Authorization头！'
                raise exceptions.AuthenticationFailed(msg)
            # 如果auth长度大于2，返回错误信息
            elif len(auth) > 2:
                msg = '不可用的Authorization头, Authorization头不可包含空格！'
                raise exceptions.AuthenticationFailed(msg)

            try:
                # 解密的算法和key必须和加密的算法保持一致
                jwt_token = auth[1]
                jwt_info = jwt.decode(jwt_token, key=settings.SECRET_KEY, algorithms="HS256")
                userid = jwt_info.get('userid')
                try:
                    # 绑定当前user到request对象上
                    user = OAUser.objects.get(pk=userid)
                    # setattr(request, 'user', user)  # setattr: 给request对象绑定一个user属性
                    # 中间件无需返回数据，会自动执行，如果返回数据，反而导致视图无法执行
                    # return user, jwt_token

                    # 注意: 这个是将user和jwt_token绑定到Django内置的HttpRequest对象，而后续使用的是DRF封装的Request对象
                    # 在authentications.py中的UserTokenAuthentication类中，会将user和jwt_token绑定到DRF封装的Request对象
                    request.user = user
                    request.auth = jwt_token
                except Exception:
                    msg = '用户不存在！'
                    raise exceptions.AuthenticationFailed(msg)
            except ExpiredSignatureError:
                msg = 'JWT token已过期！'
                raise exceptions.AuthenticationFailed(msg)
        except Exception as e:
            print(e)
            return JsonResponse({"detail": "请先登录！"}, status=HTTP_403_FORBIDDEN)
