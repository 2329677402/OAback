#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/17 下午4:35
@ Author      : Poco Ray
@ File        : initabsenttype.py
@ Description : 初始化请假类型数据, 终端执行命令: python manage.py initabsenttype
"""
from django.core.management.base import BaseCommand
from apps.absent.models import AbsentType


class Command(BaseCommand):

    def handle(self, *args, **options):
        absent_types = ["事假", "病假", "年假", "婚假", "产假", "陪产假", "丧假", "调休", "其他"]
        absents = []
        for absent_type in absent_types:
            absent = AbsentType(name=absent_type)
            absents.append(absent)
        AbsentType.objects.bulk_create(absents)  # bulk_create: 批量创建数据
        self.stdout.write(self.style.SUCCESS("初始化请假类型数据成功！"))
