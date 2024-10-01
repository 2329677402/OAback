#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/30 下午7:42
@ Author      : Poco Ray
@ File        : serializers.py
@ Description : 校验上传的图片
"""

from rest_framework import serializers
from django.core.validators import FileExtensionValidator, get_available_image_extensions


class UploadImageSerializer(serializers.Serializer):
    """
    ImageField: 校验上传的文件是否为图片
    Tips: 1. django.forms.fields.ImageField 内部使用了 PIL（Python Imaging Library）来处理图像的验证和处理。即使你在代码中没有直接使用 Pillow，Django 也依赖它来进行与图像相关的操作。
    2. 使用了 ImageField 来验证上传的图片。这个字段需要 Pillow 才能正常工作.
    3. 通过 `pip install django` 的方式不会自动安装 `Pillow` 包。虽然 `Pillow` 是处理图像上传和验证的常用库，但它并不是 Django 的强制依赖项。因此，你需要手动安装 `Pillow`。

    """
    image = serializers.ImageField(
        # validators=[FileExtensionValidator(get_available_image_extensions())], # 限制文件格式, 只能是图片格式
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])],  # 限制图片格式
        error_messages={
            'required': '请上传图片!',
            'invalid_image': '请上传图片文件!',
            'invalid_extension': '图片格式不支持, 请上传 jpg/jpeg/png/gif 格式的图片!',
        }
    )

    @staticmethod
    def validate_image(value):
        """校验图片"""
        max_size = 0.5 * 1024 * 1024  # 图片最大为0.5MB
        image_size = value.size  # 获取上传的图片大小
        # 限制图片的大小
        if image_size > max_size:
            raise serializers.ValidationError('图片大小不能超过0.5MB!')
        return value
