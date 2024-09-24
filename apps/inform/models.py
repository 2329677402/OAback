#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/24 下午11:38
@ Author      : Poco Ray
@ File        : models.py
@ Description : 创建通知相关模型
"""

from django.db import models
from apps.oaauth.models import OAUser, OADepartment


class Inform(models.Model):
    """通知模型"""
    title = models.CharField(max_length=100, verbose_name='标题')  # 通知标题
    content = models.TextField(verbose_name='内容')  # 通知内容
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')  # 创建时间
    # 如果前端上传的departments中包含了0, 比如[0], 那么就表示该通知是所有部门可见
    public = models.BooleanField(default=False, verbose_name='是否公开')  # 是否公开
    author = models.ForeignKey(OAUser, on_delete=models.CASCADE, related_name='informs',
                               related_query_name='informs')  # 发布人
    # departments: 序列化的时候用, 前端上传部门id, 后端通过department_ids获取部门对象
    departments = models.ManyToManyField(OADepartment, related_name='informs', related_query_name='informs')  # 部门

    class Meta:
        ordering = ['-create_time']


class InformRead(models.Model):
    """通知阅读模型"""
    inform = models.ForeignKey(Inform, on_delete=models.CASCADE, related_name='reads',
                               related_query_name='reads')  # 通知文章
    user = models.ForeignKey(OAUser, on_delete=models.CASCADE, related_name='reads', related_query_name='reads')  # 阅读人
    read_time = models.DateTimeField(auto_now_add=True, verbose_name='阅读时间')  # 阅读时间

    class Meta:
        ordering = ['-read_time']
        unique_together = ('inform', 'user')  #
