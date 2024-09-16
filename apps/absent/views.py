#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/17 上午12:46
@ Author      : Poco Ray
@ File        : views.py
@ Description : 实现考勤相关视图
"""
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from .models import *
from .serializers import AbsentSerializer


# 1、发起考勤(create)
# 2、处理考勤(update)
# 3、查看自己的考勤记录(list?who=my)
# 4、查看下属的考勤记录(list?who=sub)

class AbsentViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    queryset = Absent.objects.all()
    serializer_class = AbsentSerializer
