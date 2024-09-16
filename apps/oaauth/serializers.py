#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/17 上午12:47
@ Author      : Poco Ray
@ File        : serializers.py
@ Description : 实现用户相关序列化器
"""

from rest_framework import serializers
from .models import OAUser, UserStatusChoices, OADepartment
from rest_framework import exceptions


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    email = serializers.EmailField(required=True, error_messages={"required": "请输入邮箱"})  # 邮箱
    password = serializers.CharField(max_length=20, min_length=6, required=True,
                                     error_messages={"required": "请输入密码"})  # 密码

    def validate(self, attrs):
        # 校验邮箱和密码在数据库中是否存在 OR 是否正确, attrs参数是前端传递过来的数据, 包含了email和password字段
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            # first()方法返回查询集的第一个对象, 如果查询集为空, 则返回None
            user = OAUser.objects.filter(email=email).first()
            if not user:
                raise serializers.ValidationError("请输入正确的邮箱！")
            if not user.check_password(password):
                raise serializers.ValidationError("请输入正确的密码！")
            # 判断用户状态
            if user.status == UserStatusChoices.UNACTIVATED:
                raise serializers.ValidationError("该用户尚未激活！")
            elif user.status == UserStatusChoices.LOCKED:
                raise serializers.ValidationError("该用户已被锁定, 请联系管理员！")
            # 为了节省执行SQL语句的次数, 这里将user对象保存在attrs中, 在视图中可以直接使用
            attrs["user"] = user
        else:
            raise serializers.ValidationError("请输入邮箱或密码！")
        return attrs


class DepartmentSerializer(serializers.ModelSerializer):
    """部门序列化器"""

    class Meta:
        model = OADepartment
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""

    # 嵌套序列化器, 用于序列化外键字段, 能够直接包含 OADepartment 对象的详细信息，而不是仅仅包含一个外键 ID。这使得前端在处理数据时更加直观和方便。
    department = DepartmentSerializer()

    class Meta:
        model = OAUser
        # 排除字段, password不能返回给前端, groups和user_permissions字段是django内置字段, 未使用到不需要返回
        exclude = ("password", "groups", "user_permissions")


class ResetPwdSerializer(serializers.Serializer):
    """重置密码序列化器"""
    old_pwd = serializers.CharField(max_length=20, min_length=6)  # 旧密码
    new_pwd = serializers.CharField(max_length=20, min_length=6)  # 新密码
    confirm_pwd = serializers.CharField(max_length=20, min_length=6)  # 确认密码

    def validate(self, attrs):
        # 注意: attrs.get()和attrs[]的区别,
        # 如果指定key不存在, attrs[]会报错, 而attrs.get()会返回None(或者指定的默认值)，更加安全
        old_pwd = attrs.get("old_pwd")
        new_pwd = attrs.get("new_pwd")
        confirm_pwd = attrs.get("confirm_pwd")

        user = self.context.get("request").user
        if not user.check_password(old_pwd):
            raise exceptions.ValidationError("旧密码错误！")

        if new_pwd != confirm_pwd:
            raise exceptions.ValidationError("两次密码不一致！")
        return attrs