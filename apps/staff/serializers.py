#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/10/2 下午8:10
@ Author      : Poco Ray
@ File        : serializers.py
@ Description : 实现员工相关序列化器
"""
from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from django.contrib.auth import get_user_model

OAUser = get_user_model()  # 获取用户模型


class AddStaffSerializer(serializers.Serializer):
    """添加员工校验"""
    realname = serializers.CharField(max_length=20, error_messages={'required': '请输入姓名!',
                                                                    'max_length': '姓名长度不能超过20个字符!'})
    email = serializers.EmailField(error_messages={'required': '请输入邮箱!', 'invalid': '邮箱格式错误!'})
    password = serializers.CharField(max_length=20, error_messages={'required': '请输入密码!',
                                                                    'max_length': '密码长度不能超过20个字符!'})

    def validate(self, attrs):
        """自定义校验"""
        email = attrs.get('email')
        request = self.context.get('request')
        # 1. 验证邮箱是否已存在
        if OAUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('邮箱已存在!')

        # 2. 验证当前用户是否是部门的leader
        if request.user.department.leader.uid != request.user.uid:
            raise serializers.ValidationError('您不是部门负责人, 无法添加员工!')

        return attrs


class ActivateStaffSerializer(serializers.Serializer):
    """激活员工账号校验"""
    email = serializers.EmailField(error_messages={'required': '请输入邮箱!', 'invalid': '邮箱格式错误!'})
    password = serializers.CharField(max_length=20, error_messages={'required': '请输入密码!',
                                                                    'max_length': '密码长度不能超过20个字符!'})

    def validate(self, attrs):
        """自定义校验"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = OAUser.objects.filter(email=email).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError('邮箱或密码错误!')
        attrs['user'] = user
        return attrs


class StaffUploadSerializer(serializers.Serializer):
    """员工信息上传校验"""
    file = serializers.FileField(
        validators=[FileExtensionValidator(['xls', 'xlsx'])],  # 限制文件格式
        error_messages={
            'required': '请上传文件!',
            'invalid_extension': '文件格式不支持, 请上传 xls/xlsx 格式的文件!',
        })
