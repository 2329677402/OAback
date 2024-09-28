#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/29 上午1:08
@ Author      : Poco Ray
@ File        : views.py
@ Description : 实现员工相关视图, 提供部门列表
"""

from django.shortcuts import render
from rest_framework.generics import ListAPIView
from apps.oaauth.models import OADepartment
from apps.oaauth.serializers import DepartmentSerializer


class DepartmentListView(ListAPIView):
    """部门列表视图"""
    queryset = OADepartment.objects.all()
    serializer_class = DepartmentSerializer
