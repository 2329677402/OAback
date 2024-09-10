import jwt
import time
from django.conf import settings
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework import exceptions
from jwt.exceptions import ExpiredSignatureError
from .models import OAUser


def generate_jwt(user):
    """功能: 生成jwt token"""
    timestamp = int(time.time()) + 60 * 60 * 24 * 7
    # exp是一个特殊的参数, 用于表示token过期的时间
    token = jwt.encode({"userid": user.pk, "exp": timestamp}, key=settings.SECRET_KEY, algorithm="HS256")
    return token


class JWTAuthentication(BaseAuthentication):
    """
    功能: 校验JWT
    请求头中：
    Authorization: JWT 401f7ac837da42b97f613d789819ff93537bee6a
    """

    keyword = 'JWT'

    def authenticate(self, request):
        # 从请求头中获取Authorization
        # auth: ['JWT','401f7ac837da42b97f613d789819ff93537bee6a']
        auth = get_authorization_header(request).split()

        # 如果auth为空或者auth[0]不等于JWT，返回None
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        # 如果auth长度为1，返回错误信息
        if len(auth) == 1:
            msg = '不可用的Authorization头！'
            raise exceptions.AuthenticationFailed(msg)
        # 如果auth长度大于2，返回错误信息
        elif len(auth) > 2:
            msg = '不可用的Authorization头, Authorization头不可包含空格！'
            raise exceptions.AuthenticationFailed(msg)

        try:
            # 解密的算法和key必须和加密的算法保持一致
            jwt_token = auth[1]
            jwt_info = jwt.decode(jwt_token, key=settings.SECRET_KEY, algorithms="HS256")
            userid = jwt_info.get('userid')
            try:
                # 绑定当前user到request对象上
                user = OAUser.objects.get(pk=userid)
                setattr(request, 'user', user)  # setattr: 给request对象绑定一个user属性
                return user, jwt_token
            except Exception:
                msg = '用户不存在！'
                raise exceptions.AuthenticationFailed(msg)
        except ExpiredSignatureError:
            msg = 'token已过期！'
            raise exceptions.AuthenticationFailed(msg)
