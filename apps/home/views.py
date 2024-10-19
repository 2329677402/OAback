#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/10/8 下午8:07
@ Author      : Poco Ray
@ File        : views.py
@ Description : 首页视图
"""
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.absent.models import Absent
from apps.inform.models import Inform, InformRead
from django.db.models import Q, Prefetch, Count
from apps.inform.serializers import InformSerializer
from apps.absent.serializers import AbsentSerializer
from apps.oaauth.models import OADepartment
from django.views.decorators.cache import cache_page  # 缓存页面数据
from django.utils.decorators import method_decorator  # 方法装饰器


# 不同的视图函数, 使用缓存方法也不同
# 1. 对应函数视图, 使用cache_page装饰器
# 2. 对应类视图, 使用method_decorator装饰器, 并传入cache_page方法
@cache_page(60 * 15)  # 缓存15分钟
def cache_demo_view(request):
    return Response({'message': '缓存页面数据'})


class LatestInformView(APIView):
    """展示最新的10条通知"""

    @method_decorator(cache_page(60 * 15))  # 缓存15分钟
    def get(self, request):
        current_user = request.user
        reads_queryset = InformRead.objects.filter(user_id=current_user.uid)  # 当前用户的阅读记录
        # 返回公共的, 或者是自己部门的通知
        # 使用prefetch_related方法, 一次性查询出所有的阅读记录和部门信息, 减少数据库查询次数
        # Prefetch方法用于指定一个自定义查询集, 以及一个自定义查询集的名称, 这样就返回自己的阅读记录, 而不是所有人的阅读记录
        informs = Inform.objects.prefetch_related(Prefetch('reads', queryset=reads_queryset), 'departments').filter(
            Q(public=True) | Q(departments=current_user.department))[:10]
        serializer = InformSerializer(informs, many=True)
        return Response(serializer.data)


class LatestAbsentView(APIView):
    """展示最新的10条缺勤记录"""

    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        # 董事会的人可以看到所有人的缺勤记录, 其他人只能看到自己部门的缺勤记录
        current_user = request.user
        queryset = Absent.objects.all()
        if current_user.department.name != '董事会':
            # requester__department_id: __表示跨表查询, requester是Absent表中的外键, department_id是OAUser表中的字段
            queryset = queryset.filter(
                requester__department_id=current_user.department_id)  # 过滤出缺勤人员所在部门id与当前用户部门id一致的记录
        queryset = queryset[:10]
        serializer = AbsentSerializer(queryset, many=True)
        return Response(serializer.data)


class DepartmentStaffCountView(APIView):
    """展示各部门员工数量"""

    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        # annotate方法用于给查询集中的每个对象添加一个新的自定义字段(staff_count), 该字段的值是一个聚合函数的结果
        rows = OADepartment.objects.annotate(staff_count=Count('staffs')).values('name', 'staff_count')
        # print(rows)  # <QuerySet [{'name': '董事会', 'staff_count': 3}, {'name': '产品研发部', 'staff_count': 2}, {'name': '运营部', 'staff_count': 2}, {'name': '销售部', 'staff_count': 1}, {'name': '人事部', 'staff_count': 1}, {'name': '财务部', 'staff_count': 2}]>
        print('=' * 10)
        return Response(rows)


class HealthCheckView(APIView):
    """
    健康检查视图
    后续可以通过/api/home/health来检查服务是否正常
    """
    @staticmethod
    def get(request):
        return Response({"code": 200})