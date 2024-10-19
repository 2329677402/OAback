#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/10/3 下午1:38
@ Author      : Poco Ray
@ File        : tasks.py
@ Description : 使用Celery实现异步发送邮件
"""

from oaback import celery_app
from django.core.mail import send_mail
from django.conf import settings


@celery_app.task(name='send_mail_task')
def send_mail_task(email, subject, message):
    send_mail(subject, recipient_list=[email], message=message,
              from_email=settings.DEFAULT_FROM_EMAIL)
