from django.db import models
from django.contrib.auth.models import User, AbstractBaseUser, PermissionsMixin, UserManager, BaseUserManager
from django.contrib.auth.hashers import make_password
from shortuuidfield import ShortUUIDField


class UserStatusChoices(models.IntegerChoices):
    """用户状态"""
    ACTIVATED = 1  # 已激活
    UNACTIVATED = 2  # 未激活
    LOCKED = 3  # 被锁定


class OAUserManager(BaseUserManager):
    """重写UserManager模型"""
    use_in_migrations = True

    def _create_user(self, realname, email, password, **extra_fields):
        """创建并保存用户"""
        if not realname:
            raise ValueError("请设置用户的真实姓名！")
        email = self.normalize_email(email)
        user = self.model(realname=realname, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, realname, email=None, password=None, **extra_fields):
        """创建普通用户"""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(realname, email, password, **extra_fields)

    def create_superuser(self, realname, email=None, password=None, **extra_fields):
        """创建超级用户"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("status", UserStatusChoices.ACTIVATED)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("超级用户必须设置is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("超级用户必须设置is_superuser=True.")

        return self._create_user(realname, email, password, **extra_fields)


# 重写User模型
class OAUser(AbstractBaseUser, PermissionsMixin):
    """
    自定义User模型, blank=True表示可以为空
    AbstractBaseUser: 用于自定义User模型
    PermissionsMixin: 用于自定义User模型的权限
    """
    uid = ShortUUIDField(primary_key=True)  # 用户ID
    realname = models.CharField(max_length=150, unique=False)  # 真实姓名
    email = models.EmailField(unique=True, blank=False)  # 邮箱
    telephone = models.CharField(max_length=11, blank=True)  # 电话
    is_staff = models.BooleanField(default=True)  # 是否是员工
    # 只需关注status字段即可, 无需关注is_active字段, 保留is_active字段是为了兼容django的认证系统
    status = models.IntegerField(choices=UserStatusChoices, default=UserStatusChoices.UNACTIVATED)  # 用户状态
    is_active = models.BooleanField(default=True)  # 是否激活
    date_joined = models.DateTimeField(auto_now_add=True)  # 注册时间
    department = models.ForeignKey("OADeparment", on_delete=models.SET_NULL, null=True, related_name='staffs',
                                   related_query_name='staffs')  # 所属部门

    # 在后续使用objects, 会调用OAUserManager中的方法, 无需使用self
    objects = OAUserManager()

    EMAIL_FIELD = "email"
    # USERNAME_FIELD是用来做鉴权的, 会把authenticate()方法中的username参数传递给USERNAME_FIELD指定的字段
    # from django.contrib.auth import authenticate
    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS: 指定创建用户时必须填写的字段, 但是不能重复包含USERNAME_FIELD和EMAIL_FIELD已经设置的字段
    REQUIRED_FIELDS = ["realname", "password"]

    def clean(self):
        """对email字段进行格式化"""
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """返回真实姓名"""
        return self.realname

    def get_short_name(self):
        """返回真实姓名"""
        return self.realname


class OADeparment(models.Model):
    """部门模型"""
    name = models.CharField(max_length=100, unique=True)  # 部门名称
    intro = models.CharField(max_length=200)  # 部门简介
    leader = models.OneToOneField(OAUser, on_delete=models.SET_NULL, null=True, related_name='leader_department',
                                  related_query_name='leader_department')  # 部门领导
    manager = models.ForeignKey(OAUser, on_delete=models.SET_NULL, null=True, related_name='manager_department',
                                related_query_name='manager_department')  # 部门经理
