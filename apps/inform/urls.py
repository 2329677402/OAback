#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/25 上午12:52
@ Author      : Poco Ray
@ File        : urls.py
@ Description : 创建通知相关路由
"""
from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path

app_name = 'inform'

# 创建路由对象
router = DefaultRouter(trailing_slash=False)  # 禁用url末尾斜杠
router.register('inform', views.InformViewSet, basename='inform')  # 注册通知视图集

urlpatterns = [
    path('inform/read', views.ReadInformView.as_view(), name='inform_read'),  # 阅读量统计
] + router.urls
