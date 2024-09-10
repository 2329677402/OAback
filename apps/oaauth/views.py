from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import LoginSerializer
from datetime import datetime
from .authentications import generate_jwt
from rest_framework.response import Response
from rest_framework import status


class LoginView(APIView):
    def post(self, request):
        # 1、验证数据是否可用
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get("user")
            user.last_login = datetime.now()
            user.save()
            token = generate_jwt(user)
            return Response({"token": token})
        else:
            print(serializer.errors)
            return Response({"msg": "参数校验失败！"}, status=status.HTTP_400_BAD_REQUEST)
