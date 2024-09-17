#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/17 上午12:46
@ Author      : Poco Ray
@ File        : models.py
@ Description : 导入考勤相关模型
"""

from django.db import models
from django.contrib.auth import get_user_model

OAUser = get_user_model()


class AbsentStatusChoices(models.IntegerChoices):
    """请假状态"""
    WAITING = 1  # 审批中
    PASS = 2  # 通过
    REJECT = 3  # 驳回


class AbsentType(models.Model):
    """请假类型表"""
    name = models.CharField(max_length=100)  # 考勤类型名称
    create_time = models.DateTimeField(auto_now_add=True)  # 类型创建时间


class Absent(models.Model):
    """请假记录表"""
    # 1、标题
    title = models.CharField(max_length=200)
    # 2、请假详细内容
    request_content = models.TextField()
    # 3、请假类型(事假、病假)
    absent_type = models.ForeignKey(AbsentType, on_delete=models.CASCADE, related_name="absents",
                                    related_query_name="absents")
    # Tips: 如果在一个模型中有多个字段对同一个模型引用了外键，那么必须指定related_name为不同的值
    # 4、发起人
    requester = models.ForeignKey(OAUser, on_delete=models.CASCADE, related_name="my_absents",
                                  related_query_name="my_absents")
    # Tips: 审批人可以为空，如果是董事会的leader发起的请假，那么审批直接通过
    # 5、审批人
    responder = models.ForeignKey(OAUser, on_delete=models.CASCADE, related_name="sub_absents",
                                  related_query_name="sub_absents", null=True)
    # 6、审批状态
    status = models.IntegerField(choices=AbsentStatusChoices, default=AbsentStatusChoices.WAITING)
    # 7、请假开始日期
    start_date = models.DateField()
    # 8、请假结束日期
    end_date = models.DateField()
    # 9、请假发起时间
    create_time = models.DateTimeField(auto_now_add=True)
    # 10、审批回复内容，表单中可以为空
    response_content = models.TextField(blank=True)
