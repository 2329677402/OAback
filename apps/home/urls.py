#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/10/8 下午8:08
@ Author      : Poco Ray
@ File        : urls.py
@ Description : 首页路由
"""
from django.urls import path
from .views import *

app_name = 'home'

urlpatterns = [
    path('latest/inform', LatestInformView.as_view(), name='latest_inform'),
    path('latest/absent', LatestAbsentView.as_view(), name='latest_absent'),
    path('department/staff/count', DepartmentStaffCountView.as_view(), name='department_staff_count'),
]
