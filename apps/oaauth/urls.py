#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/10 下午9:42
@ Author      : Poco Ray
@ File        : urls.py
@ Description : 实现登录路由映射
"""
from django.urls import path
from . import views

app_name = 'oaauth'

urlpatterns = [
    path('login', views.LoginView.as_view(), name='login'),
    path('resetpwd', views.ResetPwdView.as_view(), name='resetpwd'),
]
