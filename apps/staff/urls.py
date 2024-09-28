#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/29 上午1:10
@ Author      : Poco Ray
@ File        : urls.py
@ Description : 员工, 部门相关路由
"""

from django.urls import path
from .views import DepartmentListView

app_name = 'staff'


urlpatterns = [
    path('departments', DepartmentListView.as_view(), name='departments'),
]
