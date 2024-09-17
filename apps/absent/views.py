#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/17 上午12:46
@ Author      : Poco Ray
@ File        : views.py
@ Description : 实现考勤相关视图
"""
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from .models import AbsentType
from .utils import get_responder
from apps.oaauth.serializers import UserSerializer


# 1、发起考勤(create)
# 2、处理考勤(update)
# 3、查看自己的考勤记录(list?who=my)
# 4、查看下属的考勤记录(list?who=sub)

class AbsentViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    queryset = Absent.objects.all()
    serializer_class = AbsentSerializer

    def update(self, request, *args, **kwargs):
        """
        问题: DRF框架中，默认情况下，如果要修改某条数据，必须传递所有字段
        解决: 如果只想修改某个或某部分字段，重写update方法，将partial属性设置为True
        """
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        问题: 查询考勤记录时会返回数据库所有的数据
        解决: 重写list方法，根据不同的查询参数返回不同的考勤记录
        """
        queryset = self.get_queryset()
        who = request.query_params.get("who")
        if who and who == "sub":
            result = queryset.filter(responder=request.user)  # 下属的考勤记录
        else:
            result = queryset.filter(requester=request.user)  # 自己的考勤记录
        # 如果想要将数据返回给前端，需要将数据序列化
        serializer = self.serializer_class(result, many=True)
        return Response(data=serializer.data)


class AbsentTypeView(APIView):
    """提供API接口给前端，用于显示员工需要请假的类型"""

    @staticmethod
    def get(request):
        types = AbsentType.objects.all()  # 获取所有的请假类型
        serializer = AbsentTypeSerializer(types, many=True)  # 将获取到的数据序列化成JSON格式
        return Response(data=serializer.data)


class ResponderView(APIView):
    """提供API接口给前端，自动获取当前账号的审批人"""

    @staticmethod
    def get(request):
        responder = get_responder(request)  # 获取当前账号的审批人
        # serializer: 如果序列化的对象是一个None，那么不会报错，而是返回一个包含除了主键外的所有字段的空字典
        serializer = UserSerializer(responder)  # 将获取到的数据序列化成JSON对象
        return Response(data=serializer.data)
