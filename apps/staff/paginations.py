#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/10/3 下午9:40
@ Author      : Poco Ray
@ File        : paginations.py
@ Description : 实现员工列表单个页面的分页器, 以区分settings.py中的全局分页器
"""
from rest_framework.pagination import PageNumberPagination


class StaffListPagination(PageNumberPagination):
    """员工列表分页器"""
    page_query_param = 'page'  # 页码参数
    page_size_query_param = 'size'  # 每页显示条数参数
    page_size = 10  # 每页显示 x 条数据
    # max_page_size = 10  # 每页最多显示 x 条数据
