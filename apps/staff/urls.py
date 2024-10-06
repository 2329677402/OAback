#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/29 上午1:10
@ Author      : Poco Ray
@ File        : urls.py
@ Description : 员工, 部门相关路由
"""

from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter

app_name = 'staff'
router = DefaultRouter(trailing_slash=False)
router.register(r'staff', StaffViewSet, basename='staff')

urlpatterns = [
    path('departments', DepartmentListView.as_view(), name='departments'),
    # path('staff', StaffView.as_view(), name='staff'),
    path('activate', ActivateStaffView.as_view(), name='activate'),
    path('download', StaffDownloadView.as_view(), name='download'),
    path('upload', StaffUploadView.as_view(), name='upload'),
    path('test/celery', TestCeleryView.as_view(), name='test_celery'),
] + router.urls
