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
router = DefaultRouter()
router.register("absent", views.AbsentViewSet, basename="absent")

urlpatterns = [] + router.urls
