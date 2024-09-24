#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/25 上午12:50
@ Author      : Poco Ray
@ File        : views.py
@ Description : 创建通知相关视图集
"""
from rest_framework import viewsets
from .models import Inform
from .serializers import InformSerializer


class InformViewSet(viewsets.ModelViewSet):
    """通知视图集"""
    queryset = Inform.objects.all()
    serializer_class = InformSerializer
