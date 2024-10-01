#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/30 下午9:22
@ Author      : Poco Ray
@ File        : urls.py
@ Description : 功能描述
"""
from django.urls import path
from . import views

app_name = 'image'

urlpatterns = [
    path('upload', views.UploadImageView.as_view(), name='upload')
]
