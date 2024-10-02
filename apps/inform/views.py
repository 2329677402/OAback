#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/25 上午12:50
@ Author      : Poco Ray
@ File        : views.py
@ Description : 创建通知相关视图集
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Inform, InformRead
from .serializers import InformSerializer, ReadInformSerializer
from django.db.models import Q
from django.db.models import Prefetch


class InformViewSet(viewsets.ModelViewSet):
    """通知视图集"""
    queryset = Inform.objects.all()
    serializer_class = InformSerializer

    def get_queryset(self):
        """
        重写获取通知列表的方法

        通知列表, 哪些人可以看到通知
        1. inform.public=True, 公开通知
        2. inform.departments=request.user.departments, 部门通知,包含当前用户所在部门
        3. inform.author=request.user
        """

        # 如果多个条件的并查, 那么就需要用到Q对象
        # queryset = self.queryset.filter(
        #     Q(public=True) | Q(departments=self.request.user.department) | Q(author=self.request.user))
        # for inform in queryset:
        #     inform.is_read=InformRead.objects.filter(inform=inform, user=self.request.user).exists()
        # return queryset

        # 优化: 使用prefetch_related方法, 一次性查询出所有的阅读记录和部门信息, 减少数据库查询次数
        # select_related方法与之类似, 但仅适用于一对一或一对多关系, prefetch_related适用于多对多或多对一关系
        # Prefetch方法用于指定一个自定义查询集, 以及一个自定义查询集的名称
        user = self.request.user  # 当前登录用户
        reads_queryset = InformRead.objects.filter(user_id=user.uid)  # 当前用户的阅读记录
        queryset = self.queryset.select_related('author').prefetch_related(
            Prefetch('reads', queryset=reads_queryset), 'departments'
        ).filter(
            Q(public=True) | Q(departments=user.department) | Q(author=user)
        ).distinct()
        return queryset

    def destroy(self, request, *args, **kwargs):
        """重写删除通知的方法, 只有该篇通知的作者才能删除通知"""
        instance = self.get_object()
        if instance.author.uid == request.user.uid:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def retrieve(self, request, *args, **kwargs):
        """重写获取通知详情的方法"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        # 计算某个通知的阅读次数，并将其存储在返回数据的 `read_count` 字段中
        data['read_count'] = InformRead.objects.filter(inform_id=instance.id).count()
        return Response(data=data)


class ReadInformView(APIView):
    """阅读量统计"""

    @staticmethod
    def post(request):
        """阅读通知"""
        serializer = ReadInformSerializer(data=request.data)
        if serializer.is_valid():
            inform_pk = serializer.validated_data.get('inform_pk')  # 通知id
            # 判断是否已经阅读过该通知
            if InformRead.objects.filter(inform_id=inform_pk, user_id=request.user.uid).exists():
                return Response(data={'detail': '已阅读'}, status=status.HTTP_200_OK)
            else:
                try:
                    InformRead.objects.create(inform_id=inform_pk, user_id=request.user.uid)
                    return Response(data={'detail': '阅读成功'}, status=status.HTTP_201_CREATED)
                except Exception as e:
                    print(e)
                    return Response(data={'detail': '阅读失败!'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data={'detail': list(serializer.errors.values())[0][0]}, status=status.HTTP_400_BAD_REQUEST)
