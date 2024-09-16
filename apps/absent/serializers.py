#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/17 上午12:46
@ Author      : Poco Ray
@ File        : serializers.py
@ Description : 实现考勤相关序列化器
"""

from rest_framework import serializers
from .models import Absent, AbsentType, AbsentStatusChoices
from apps.oaauth.serializers import UserSerializer
from rest_framework import exceptions


class AbsentTypeSerializer(serializers.ModelSerializer):
    """考勤类型序列化器"""

    class Meta:
        model = AbsentType
        fields = "__all__"


class AbsentSerializer(serializers.ModelSerializer):
    """考勤序列化器"""
    # 重写absent_type字段，前端提交表单到数据库中，应该提交的是一个id，而不是请假类型
    # read_only=True: 这个参数，只会将ORM模型序列化成字典时，将absent_type字段序列化成字典
    # write_only=True: 这个参数，只会在将data进行校验的时候才会用到
    absent_type = AbsentTypeSerializer(read_only=True)
    # absent_type_id, 这个字段只会在前端传过来的时候进行校验，而不会在数据库中生成，因为设置了write_only=True
    # 而且models.py中设置了absent_type字段为外键，数据库中生成的字段名为absent_type_id，所以这里的absent_type_id只做校验
    absent_type_id = serializers.IntegerField(write_only=True)
    requester = UserSerializer(read_only=True)
    responder = UserSerializer(read_only=True)

    class Meta:
        model = Absent
        fields = "__all__"

    def validate_absent_type_id(self, value):
        # 验证absent_type_id字段是否在数据库中存在
        if not AbsentType.objects.filter(pk=value).exists():
            raise exceptions.ValidationError(detail="考勤类型不存在！")
        return value

    def create(self, validated_data):
        """新增考勤记录时，执行create方法"""
        request = self.context.get("request")  # 获取请求对象
        user = request.user  # 获取当前登录用户
        # 获取审批人

        # 1、如果是部门的leader发起的请假，那么审批人是董事会的manager(董事会leader请假直接通过)
        # 2、如果是员工发起的请假，那么审批人是各自部门的leader
        if user.department.leader.uid == user.uid:
            if user.department.name == "董事会":
                responder = None
            else:
                responder = user.department.manager
        else:
            responder = user.department.leader

        if responder is None:
            validated_data["status"] = AbsentStatusChoices.PASS  # 董事会leader请假直接通过
        absent = Absent.objects.create(**validated_data, requester=user, responder=responder)
        return absent

    def update(self, instance, validated_data):
        """更新考勤记录时，执行update方法"""
        # 如果考勤记录已经开始审批，那么无法修改
        if instance.status != AbsentStatusChoices.WAITING:
            raise exceptions.APIException(detail="当前考勤记录已经开始审批，无法修改！")

        request = self.context.get("request")  # 获取请求对象
        user = request.user  # 获取当前登录用户

        # 如果当前用户不是对应的审批人，那么无法修改
        if instance.responder.uid != user.uid:
            raise exceptions.AuthenticationFailed(detail="当前用户无权限修改该考勤记录！")

        # 如果是对应的审批人，执行审批操作
        instance.status = validated_data.get("status")
        instance.response_content = validated_data.get("response_content")
        instance.save()
        return instance
