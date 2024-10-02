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

from .models import Inform, InformRead
from .serializers import InformSerializer
from django.db.models import Q


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
        user = self.request.user  # 当前登录用户
        queryset = self.queryset.select_related('author').prefetch_related('reads', 'departments').filter(
            Q(public=True) | Q(departments=user.department) | Q(author=user)).distinct()
        return queryset

    def destroy(self, request, *args, **kwargs):
        """
        重写删除通知的方法, 只有该篇通知的作者才能删除通知
        """
        instance = self.get_object()
        if instance.author.uid == request.user.uid:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
