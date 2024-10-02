#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/24 下午11:38
@ Author      : Poco Ray
@ File        : serializers.py
@ Description : 创建通知相关序列化器
"""

from rest_framework import serializers
from .models import Inform, InformRead
from apps.oaauth.serializers import UserSerializer, DepartmentSerializer
from apps.oaauth.models import OADepartment


class InformReadSerializer(serializers.ModelSerializer):
    """通知阅读序列化器"""

    class Meta:
        model = InformRead
        fields = '__all__'


class InformSerializer(serializers.ModelSerializer):
    """通知序列化器"""
    author = UserSerializer(read_only=True)
    departments = DepartmentSerializer(read_only=True, many=True)
    # departments_ids: 是一个包含部门id的列表, 如果后端要接收列表, 需要使用ListField
    department_ids = serializers.ListField(write_only=True)
    reads = InformReadSerializer(many=True, read_only=True)

    class Meta:
        model = Inform
        fields = '__all__'
        # 用于指定哪些字段在序列化时是只读的. 在validate时, 会忽略这些字段.
        read_only_fields = ('public',)  # 注意: 这里需要定义为列表或元组

    def create(self, validated_data):
        """重写保存Inform对象的create方法"""
        # 从validated_data中获取departments_ids, 并删除departments_ids
        department_ids = validated_data.pop('department_ids')
        request = self.context.get('request')

        # departments_ids: ['0', '1', '2']
        # 对列表中的某个值都做相同的操作, 可以使用map函数, map(函数, 列表)
        # def toInt(value):
        #     return int(value)
        # map(toInt, departments_ids)
        department_ids = list(map(lambda value: int(value), department_ids))
        if 0 in department_ids:
            inform = Inform.objects.create(public=True, author=request.user, **validated_data)
        else:
            departments = OADepartment.objects.filter(id__in=department_ids).all()
            inform = Inform.objects.create(public=False, author=request.user, **validated_data)
            inform.departments.set(departments)  # 清除原来的部门, 并设置过滤后的部门
            inform.save()
        return inform


class ReadInformSerializer(serializers.Serializer):
    """阅读量序列化器"""
    inform_pk = serializers.IntegerField(error_messages={'required': '请传入inform的id!'})  # 通知id
