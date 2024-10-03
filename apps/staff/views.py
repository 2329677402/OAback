#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/29 上午1:08
@ Author      : Poco Ray
@ File        : views.py
@ Description : 实现员工相关视图, 提供部门列表
"""

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.oaauth.models import OADepartment
from apps.oaauth.serializers import DepartmentSerializer
from .serializers import AddStaffSerializer
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from utils import aeser
from django.urls import reverse
from OAback.celery import debug_task
from .tasks import send_mail_task

OAUser = get_user_model()  # 获取用户模型
aes = aeser.AESCipher(settings.SECRET_KEY)  # 创建加密对象


class DepartmentListView(ListAPIView):
    """部门列表视图"""
    queryset = OADepartment.objects.all()
    serializer_class = DepartmentSerializer


class ActivateStaffView(APIView):
    """激活员工账号"""

    @staticmethod
    def get(request):
        pass


class StaffView(APIView):
    """员工视图"""

    # 员工列表
    @staticmethod
    def get(request):
        token = "unGKeqffNBqpwNP1MRzIXdnY6/l4izEmCfH0ds0KHnI="
        result = aes.decrypt(token)  # 解密token
        return Response(data={'email': result}, status=status.HTTP_200_OK)

    # 添加员工账号
    def post(self, request):
        # Tips: 1. 如果用的是视图集, 那么视图集会自动把request放到context中
        #       2. 如果是继承至APIView, 那么需要手动把request对象传递给context
        serializer = AddStaffSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            realname = serializer.validated_data.get('realname')
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            # 1. 保存员工数据
            user = OAUser.objects.create_user(realname=realname, email=email, password=password)
            user.department = request.user.department
            user.save()

            # 2. 发送激活邮件
            self.send_activate_email(email)

            return Response(data={'detail': '员工添加成功!'}, status=status.HTTP_201_CREATED)
        else:
            return Response(data={'detail': list(serializer.errors.values())[0][0]}, status=status.HTTP_400_BAD_REQUEST)

    def send_activate_email(self, email):
        """发送激活邮件"""
        token = aes.encrypt(email)  # 加密邮箱, 保存到token字符串中
        # 拼接激活path路径, 例如: /staff/activate?token=xxxx
        activate_path = reverse('staff:activate') + f'?token={token}'
        # 拼接激活url链接, 例如: http://127.0.0.1:8000/staff/activate?token=xxxx
        # build_absolute_uri: 构建绝对url路径
        activate_url = self.request.build_absolute_uri(activate_path)

        # 发送一个链接, 让用户点击这个链接后, 跳转到激活页面, 激活账号
        # 为了区分用户, 在发送链接邮件中, 这个链接中需要包含用户的邮箱
        # 针对邮箱要进行加密处理, 不能直接暴露在链接中: 使用AES加密算法
        # 请点击链接激活账号: http://127.0.0.1:8000/staff/activate?token=unGKeqffNBqpwNP1MRzIXdnY6/l4izEmCfH0ds0KHnI=
        message = f'请点击链接激活账号: {activate_url}'
        subject = '[OA System] 账号激活!'
        # send_mail(f'[OA System] 账号激活!', recipient_list=[email], message=message,
        #           from_email=settings.DEFAULT_FROM_EMAIL)
        send_mail_task.delay(email, subject, message)

class TestCeleryView(APIView):
    """测试Celery异步任务"""

    @staticmethod
    def get(request):
        # 用celery异步执行debug_task任务
        debug_task.delay()
        return Response(data={'detail': '任务已经提交!'}, status=status.HTTP_200_OK)
