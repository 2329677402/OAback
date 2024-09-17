#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/16 下午11:44
@ Author      : Poco Ray
@ File        : urls.py
@ Description : URL映射
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "absent"
# 使用DRF默认的路由器生成的URL会在末尾强制添加"/"才能访问
# 设置trailing_slash=False可以去掉末尾的"/"
router = DefaultRouter(trailing_slash=False)
# http://localhost:8000/absent/absent/
router.register("absent", views.AbsentViewSet, basename="absent")

urlpatterns = [
                  path('type', views.AbsentTypeView.as_view(), name="absenttypes"),
                  path('responder', views.ResponderView.as_view(), name="getresponder")
              ] + router.urls
