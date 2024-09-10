#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/10 下午9:40
@ Author      : Poco Ray
@ File        : views.py
@ Description : 实现登录视图
"""
from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import LoginSerializer, UserSerializer
from datetime import datetime
from .authentications import generate_jwt
from rest_framework.response import Response
from rest_framework import status


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
            print(serializer.errors)
            return Response({"msg": "参数校验失败！"}, status=status.HTTP_400_BAD_REQUEST)
