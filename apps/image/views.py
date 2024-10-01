#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/30 下午7:37
@ Author      : Poco Ray
@ File        : views.py
@ Description : 保存上传的图片
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UploadImageSerializer
from shortuuid import uuid
import os
from django.conf import settings


class UploadImageView(APIView):
    """上传图片视图"""

    @staticmethod
    def post(request):
        # 1. drf可以通过request.data直接获取请求数据
        # 2. django需要通过request.POST(表单数据)或request.FILES(文件数据)获取数据
        serializer = UploadImageSerializer(data=request.data)

        if serializer.is_valid():
            file = serializer.validated_data.get('image')
            # 生成唯一的文件名
            # splitext: 分离文件扩展名, os.path.splitext(abc.jpg) => ('abc', '.jpg')
            # filename = uuid() + os.path.splitext(file.name)[-1]
            filename = f"{uuid()}.{file.name.split('.')[-1]}"
            path = settings.MEDIA_ROOT / filename
            # 保存图片文件
            try:
                with open(path, 'wb') as f:
                    for chunk in file.chunks():
                        f.write(chunk)
            except Exception as e:
                print(e)
                # 接口返回数据需要与wangeditor保持一致: https://www.wangeditor.com/v5/menu-config.html#%E6%9C%8D%E5%8A%A1%E7%AB%AF%E5%9C%B0%E5%9D%80
                return Response({
                    "errno": 1,  # 只要不等于 0 就行
                    "message": "图片保存失败!"
                })
            file_url = f"{settings.MEDIA_URL}{filename}"
            # 接口返回数据需要与wangeditor保持一致
            return Response({
                "errno": 0,  # 注意：值是数字，不能是字符串
                "data": {
                    "url": file_url,  # 图片 src ，必须
                    "alt": "",  # 图片描述文字，非必须
                    "href": file_url  # 图片的链接，非必须
                }
            })
        else:
            print(serializer.errors.values())
            return Response({
                "errno": 1,  # 只要不等于 0 就行
                "message": list(serializer.errors.values())[0][0]
            })
