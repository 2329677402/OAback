#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/17 下午8:36
@ Author      : Poco Ray
@ File        : utils.py
@ Description : 考勤相关工具函数
"""


def get_responder(request):
    """
    功能: 获取当前账号的审批人
        1、如果是部门的leader发起的请假，那么审批人是董事会的manager(董事会leader请假直接通过)
        2、如果是员工发起的请假，那么审批人是各自部门的leader
    """
    user = request.user
    if user.department.leader.uid == user.uid:
        if user.department.name == "董事会":
            responder = None
        else:
            responder = user.department.manager
    else:
        responder = user.department.leader
    return responder
