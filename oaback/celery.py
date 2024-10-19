#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/10/2 下午10:32
@ Author      : Poco Ray
@ File        : celery.py
@ Description : Celery配置文件, 用于异步任务处理
"""
import os
from celery import Celery
from celery.signals import after_setup_logger
import logging

# 设置django的settings模块，celery会读取这个模块中的配置信息
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oaback.settings')

# 创建celery对象
app = Celery('oaback')


## 日志管理
@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add filehandler
    fh = logging.FileHandler('logs.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)


# 配置从settings.py中读取celery配置信息，所有Celery配置信息都要以CELERY_开头
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务，任务可以写在app/tasks.py中
app.autodiscover_tasks()


# 测试任务
# 1. bind=True, 在任务函数中, 第一个参数就是任务对象Task, 如果没有设置这个参数或者设置为False, 那么任务函数中就不会传递任务对象参数
# 2. ignore_result=True, 不会保存任务执行的结果
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
