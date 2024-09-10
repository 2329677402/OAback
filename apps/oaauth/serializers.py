from rest_framework import serializers
from .models import OAUser, UserStatusChoices


class LoginSerializer(serializers.Serializer):
    """
    登录序列化器
    """
    email = serializers.EmailField(required=True)  # 邮箱
    password = serializers.CharField(max_length=20, min_length=6, required=True)  # 密码

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
