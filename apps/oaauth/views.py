#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/10 下午9:40
@ Author      : Poco Ray
@ File        : views.py
@ Description : 实现登录，重置密码视图
"""
from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import LoginSerializer, UserSerializer
from datetime import datetime
from .authentications import generate_jwt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class LoginView(APIView):
    @staticmethod
    def post(request):
        # 1、验证数据是否可用
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get("user")  # user对象是传过来的email
            user.last_login = datetime.now()
            user.save()
            token = generate_jwt(user)
            return Response({"token": token, "user": UserSerializer(user).data})
        else:
            print(list(serializer.errors.values())[0][0])
            detail = (list(serializer.errors.values())[0][0])
            # drf在返回响应是非200状态码时, 会自动返回一个字典, 键为"detail", 值为错误信息
            return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)


# class AuthenticatedRequiredView(APIView):
#     permission_classes = [IsAuthenticated]  # 需要登录后才能访问该视图


class ResetPwdView(APIView):

    @staticmethod
    def post(request):
        # from rest_framework.request import Request
        # request对象是DRF封装的, rest_framework.request.Request
        # 这个对象是针对django的HttpRequest对象的封装
        return Response({"msg": "success！"})
