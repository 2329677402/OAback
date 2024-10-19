#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@ Date        : 2024/9/29 上午1:08
@ Author      : Poco Ray
@ File        : views.py
@ Description : 实现员工相关视图, 提供部门列表
"""
from django.shortcuts import render
from rest_framework import status, viewsets, mixins
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.oaauth.models import OADepartment, UserStatusChoices
from apps.oaauth.serializers import DepartmentSerializer
from .serializers import AddStaffSerializer, ActivateStaffSerializer, StaffUploadSerializer
from django.contrib.auth import get_user_model
# from django.core.mail import send_mail
from django.conf import settings
from utils import aeser
from django.urls import reverse
from oaback.celery import debug_task
from .tasks import send_mail_task
from django.views import View
from django.http.response import JsonResponse, HttpResponse
from urllib import parse
from rest_framework import exceptions
from apps.oaauth.serializers import UserSerializer
from .paginations import StaffListPagination
from datetime import datetime
import pandas as pd
import json
from django.db import transaction  # 事务处理

OAUser = get_user_model()  # 获取用户模型
aes = aeser.AESCipher(settings.SECRET_KEY)  # 创建加密对象


def send_activate_email(request, email):
    """发送激活邮件"""
    token = aes.encrypt(email)  # 加密邮箱, 保存到token字符串中
    # 拼接激活path路径, 例如: /staff/activate?token=xxxx
    # activate_path = reverse('staff:activate') + f'?token={token}'
    # 现代浏览器会自动处理 URL 编码和解码. 但是, 为了确保最大兼容性, 还是建议使用 urllib.parse.urlencode() 来处理 URL 查询字符串.
    activate_path = reverse('staff:activate') + '?' + parse.urlencode({'token': token})
    # 拼接激活url链接, 例如: http://127.0.0.1:8000/staff/activate?token=xxxx
    # build_absolute_uri: 构建绝对url路径
    activate_url = request.build_absolute_uri(activate_path)

    # 发送一个链接, 让用户点击这个链接后, 跳转到激活页面, 激活账号
    # 为了区分用户, 在发送链接邮件中, 这个链接中需要包含用户的邮箱
    # 针对邮箱要进行加密处理, 不能直接暴露在链接中: 使用AES加密算法
    # 请点击链接激活账号: http://127.0.0.1:8000/staff/activate?token=unGKeqffNBqpwNP1MRzIXdnY6/l4izEmCfH0ds0KHnI=
    message = f'请点击链接激活账号: {activate_url}'
    subject = '[OA System] 账号激活!'
    # send_mail(f'[OA System] 账号激活!', recipient_list=[email], message=message, from_email=settings.DEFAULT_FROM_EMAIL)
    send_mail_task.delay(email, subject, message)


class DepartmentListView(ListAPIView):
    """部门列表视图"""
    queryset = OADepartment.objects.all()
    serializer_class = DepartmentSerializer


# 激活员工账号流程
# 1. 用户访问激活的链接的时候, 会返回一个含有表单的页面, 视图中可以获取到token, 为了用户提交表单的时候, post函数中可以获取到token, 我们可以在返回页面之前, 先把token存储到cookie中
# 2. 校验用户上传的邮箱和密码是否正确, 并且解密token中的邮箱, 与用户提交的邮箱进行比对, 如果一致, 则成功激活员工账号
class ActivateStaffView(View):
    """激活员工账号"""

    @staticmethod
    def get(request):
        # 获取token, 并把token存储到cookie中, 方便下次用户传过来
        # 请点击链接激活账号: http://127.0.0.1:8000/staff/activate?token=wCFYYImC7yY7z7xveVuRnFPKQJ6uU8/RFrRNlWEQuv4=
        token = request.GET.get('token')
        response = render(request, 'activate.html')
        response.set_cookie('token', token)
        return response

    @staticmethod
    def post(request):
        # 从cookie中获取token
        try:
            token = request.COOKIES.get('token')
            email = aes.decrypt(token)  # 解密后的邮箱
            serializer = ActivateStaffSerializer(data=request.POST)

            if serializer.is_valid():
                form_email = serializer.validated_data.get('email')  # 表单中的邮箱
                user = serializer.validated_data.get('user')
                if email != form_email:
                    return JsonResponse({'code': 400, 'msg': '邮箱错误!'})
                user.status = UserStatusChoices.ACTIVATED  # 激活用户
                user.save()
                return JsonResponse({'code': 200, 'msg': '激活成功!'})
            else:
                detail = list(serializer.errors.values())[0][0]
                return JsonResponse({'code': 400, 'msg': detail})

        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'msg': 'token错误!'})


class StaffViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
):
    """员工视图"""
    queryset = OAUser.objects.all()
    pagination_class = StaffListPagination  # 使用员工列表分页器

    def get_serializer_class(self):
        """StaffView类中, 需要使用两个serializer, 视不同的请求方法, 返回不同的serializer"""
        if self.request.method in ['GET', 'PUT']:
            return UserSerializer  # 返回员工列表
        else:
            return AddStaffSerializer  # 添加员工账号

    # 获取员工列表
    def get_queryset(self):
        # print(self.request.query_params)  # 获取查询参数
        # # <QueryDict: {'department_id': ['1'], 'realname': ['Poco'], 'date_joined[]': ['2024-10-02', '2024-10-04'], 'page': ['1'], 'size': ['10']}>
        department_id = self.request.query_params.get('department_id')
        realname = self.request.query_params.get('realname')
        date_joined = self.request.query_params.getlist('date_joined[]')

        queryset = self.queryset
        # 返回员工列表逻辑
        # 1. 如果是董事会, 返回所有员工
        # 2. 如果不是董事会, 但是是部门leader, 返回部门员工
        # 3. 如果不是董事会, 也不是部门leader, 那么抛出403异常

        # ① 根据用户的部门ID进行查询
        user = self.request.user
        if user.department.name != '董事会':
            if user.uid != user.department.leader.uid:
                raise exceptions.PermissionDenied('您没有权限查看员工列表!')
            else:
                queryset = queryset.filter(department_id=user.department_id)
        else:
            # 如果是董事会, 根据部门ID进行查询
            if department_id:
                queryset = queryset.filter(department_id=department_id)

        # ② 根据真实姓名进行查询
        if realname:
            queryset = queryset.filter(realname__icontains=realname)

        # ③ 根据注册时间进行查询
        if date_joined:
            # 格式: ['2024-10-01', '2024-10-10']
            try:
                start_date = datetime.strptime(date_joined[0], '%Y-%m-%d')
                end_date = datetime.strptime(date_joined[1], '%Y-%m-%d')
                queryset = queryset.filter(date_joined__range=[start_date, end_date])
            except Exception as e:
                print(e)

        return queryset.order_by('-date_joined').all()

    # 添加员工账号
    def create(self, request, *args, **kwargs):
        # Tips: 1. 如果用的是视图集, 那么视图集会自动把request放到context中
        #       2. 如果是继承至APIView, 那么需要手动把request对象传递给context
        serializer = AddStaffSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            realname = serializer.validated_data.get('realname')
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            # 1. 保存员工数据
            user = OAUser.objects.create_user(realname=realname, email=email, password=password)
            user.department = request.user.department
            user.save()

            # 2. 发送激活邮件
            send_activate_email(request, email)

            return Response(data={'detail': '员工添加成功!'}, status=status.HTTP_201_CREATED)
        else:
            return Response(data={'detail': list(serializer.errors.values())[0][0]}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True  # 设置为局部更新
        return super().update(request, *args, **kwargs)


class StaffDownloadView(APIView):
    """员工数据下载"""

    @staticmethod
    def get(request):
        # /staff/download?pks=[1 ,2 ,3]
        # 需要格式: ['1', '2', '3'] -> 实际格式: [1, 2, 3]
        pks = request.query_params.get('pks')  # 需要下载的员工列表
        try:
            pks = json.loads(pks)  # JSON格式字符串 -> 列表, [1 ,2 ,3] -> ['1', '2', '3']
        except Exception as e:
            print(e)
            return Response(data={'detail': '参数错误!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 权限管理
            # 1. 董事会可以下载所有员工数据
            # 2. 部门leader只能下载本部门员工数据
            # 3. 普通员工无法下载员工数据
            current_user = request.user
            queryset = OAUser.objects
            if current_user.department.name != '董事会':
                if current_user.uid != current_user.department.leader_id:
                    # 普通员工
                    return Response(data={'detail': '您没有权限下载员工数据!'}, status=status.HTTP_403_FORBIDDEN)
                else:
                    # 部门leader
                    queryset = queryset.filter(department_id=current_user.department_id)
            # 董事会
            queryset = queryset.filter(pk__in=pks)
            # 使用values提取需要用于生成excel表格中展示的字段, 而不是全部字段
            result = queryset.values('realname', 'email', 'department__name', 'date_joined', 'status')

            ###################使用Pandas处理Excel表格#####################
            # Tips: result是一个QuerySet对象, 需要转换成python对象, 才能使用pandas进行数据处理
            staff_df = pd.DataFrame(list(result))
            staff_df.rename(
                columns={'realname': '姓名', 'email': '邮箱', 'department__name': '所属部门',
                         'date_joined': '入职日期', 'status': '状态'}, inplace=True)  # 重命名列名
            response = HttpResponse(content_type='application/xlsx')  # 设置响应头
            response['Content-Disposition'] = 'attachment; filename=员工信息.xlsx'  # 设置下载文件名
            # 将staff_df数据写入到response中
            with pd.ExcelWriter(response) as writer:
                staff_df.to_excel(writer, sheet_name='员工信息')
            return response
        except Exception as e:
            print(e)
            return Response(data={'detail': '下载失败!'}, status=status.HTTP_400_BAD_REQUEST)


class StaffUploadView(APIView):
    """员工数据上传"""

    @staticmethod
    def post(request):
        serializer = StaffUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data.get('file')

            # 判断用户的权限是否可以上传员工数据
            current_user = request.user
            if current_user.department.name != '董事会' or current_user.uid != current_user.department.leader_id:
                return Response(data={'detail': '您没有权限上传员工数据!'}, status=status.HTTP_403_FORBIDDEN)

            # 读取上传的文件, 每读取一行数据, 就创建一个OAUser对象
            staff_df = pd.read_excel(file)
            users = []  # 保存创建的员工对象
            for index, row in staff_df.iterrows():  # iterrows()方法: 迭代器, 每次循环返回一行数据
                # 获取部门信息
                if current_user.department.name != '董事会':
                    department = current_user.department  # 将OAUser对象的部门设置为部门leader所在的部门
                else:
                    try:
                        department = OADepartment.objects.filter(name=row['部门']).first()  # 将OAUser对象的部门设置为Excel中填写的部门
                        # Excel中填写未录入的部门
                        if not department:
                            return Response(data={'detail': f'{row["部门"]}不存在!'},
                                            status=status.HTTP_400_BAD_REQUEST)
                    except Exception as e:
                        print(e)
                        # Excel中的表头行或列标题中未找到“部门”列
                        return Response(data={'detail': '<部门>列标题不存在!'}, status=status.HTTP_400_BAD_REQUEST)

                # 创建员工账号
                try:
                    email = row['邮箱']
                    realname = row['姓名']
                    password = '111111'  # 默认密码
                    # Tips: 避免使用create_user方法, 考虑到当前在for循环中, 每次创建用户都会连接数据库, 会影响性能.
                    # user = OAUser.objects.create_user(email=email, realname=realname, department=department, status=UserStatusChoices.UNACTIVATED)
                    user = OAUser(email=email, realname=realname, department=department,
                                  status=UserStatusChoices.UNACTIVATED)
                    user.set_password(password)
                    users.append(user)

                except Exception as e:
                    print(e)
                    return Response(data={'detail': '请检查Excel文件中的表头行!'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # 统一把users列表中的员工数据保存到数据库中
                # 考虑到导入的数据中可能存在数据重复等特殊情况, 这里使用事务处理, 即: 要么全部成功, 要么全部失败
                with transaction.atomic():
                    OAUser.objects.bulk_create(users)
            except Exception as e:
                print(e)
                return Response(data={'detail': '员工数据导入失败!'}, status=status.HTTP_400_BAD_REQUEST)

            # 异步给每个员工发送激活邮件
            for user in users:
                send_activate_email(request, user.email)
            return Response(data={'detail': '员工数据导入成功!'}, status=status.HTTP_201_CREATED)
        else:
            detail = list(serializer.errors.values())[0][0]
            return Response(data={'detail': detail}, status=status.HTTP_400_BAD_REQUEST)


class TestCeleryView(APIView):
    """测试Celery异步任务"""

    @staticmethod
    def get(request):
        # 用celery异步执行debug_task任务
        debug_task.delay()
        return Response(data={'detail': '任务已经提交!'}, status=status.HTTP_200_OK)
