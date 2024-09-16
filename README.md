[toc]

# OAback

> 基于 `Django` 框架开发的OA系统.

## 常用命令

```shell
# 创建 django 项目
django-admin startproject [项目名称]

# 创建 django app
python manage.py startapp [app名称]

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```



## 配置问题

### 1、数据库

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'djangoa',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '3306'
    }
}
```



### 2、时区及语言

- **设置时区**: 在 `settings.py` 中，将`TIME_ZONE` 设置为 `'Asia/Shanghai'`，`USE_TZ` 设置为`False`, 关闭时区支持，这是适用于中国的时区标识符.

- **设置语言**: 将`LANGUAGE_CODE`设置改为`'zh-hans'`,可以将管理员页面语言设置为简体中文.

  ```python
  # settings.py
  
  LANGUAGE_CODE = "zh-hans"
  TIME_ZONE = "Asia/Shanghai"
  USE_I18N = True
  USE_TZ = False
  ```



### 3、中间件

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 跨域中间件, 一定要放在CommonMiddleware之前
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 前端通过Vue去渲染，不再使用Django的模板，并且使用JWT进行认证，不是通过cookie，无需开启csrf保护
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```



## 报错问题

### 1、数据库未正确识别

![image-20240909004334643](assets/image-20240909004334643.png)

**在 Django 设置中配置 pymysql**: 在 Django 项目的 `settings.py` 或 `__init__.py` 中告诉 Django 使用 `pymysql`。在文件的顶部添加以下代码：

```python
import pymysql

pymysql.install_as_MySQLdb()
```





## Tips

### 1、Meta类的作用

> Meta类在Django的序列化器和模型中用于定义一些元数据，这些元数据可以控制序列化器或模型的行为。以下是一些常见的用途：

==序列化器==：

- `model`：指定与序列化器关联的模型。
- `fields`：指定要包含在序列化器中的字段。
- `exclude`：指定要排除在序列化器之外的字段。

==模型==：  

- `db_table`：指定数据库表的名称。
- `ordering`：指定默认的排序方式。
- `verbose_name `和 `verbose_name_plural`：指定模型的单数和复数名称。

```python
# 在序列化器中使用Meta类
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = OAUser
        fields = "__all__"

# 在模型中使用Meta类
class OAUser(models.Model):
    # 模型字段定义
    class Meta:
        db_table = "oa_user"
        ordering = ["-date_joined"]
        verbose_name = "用户"
        verbose_name_plural = "用户"
```



### 2、嵌套序列化器

代码示例：

```python
class DepartmentSerializer(serializers.ModelSerializer):
    """部门序列化器"""
    
    class Meta:
        model = OADepartment
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    
    department = DepartmentSerializer()  # 嵌套序列化器, 用于序列化外键字段
    
    class Meta:
        model = OAUser
        exclude = ("password", "groups", "user_permissions")
```

  在 `UserSerializer `类中加入 `department = DepartmentSerializer()` 这行代码是为了实现嵌套序列化。嵌套序列化器用于==序列化外键字段==，使得在序列化 `OAUser `对象时，能够包含关联的 `OADepartment `对象的详细信息。  

具体来说，这样做有以下几个好处：

1. **直观的数据结构**：在序列化 `OAUser `对象时，==能够直接包含 OADepartment 对象的详细信息，而不是仅仅包含一个外键 ID==。这使得前端在处理数据时更加直观和方便。  
2. **减少查询次数**：通过嵌套序列化器，可以在一次查询中获取到关联对象的详细信息，减少了额外的数据库查询次数，提高了性能。  
3. **数据完整性**：确保在序列化过程中，关联对象的数据也能被正确地序列化和返回，保持数据的完整性。

![image-20240910232439173](assets/image-20240910232439173.png)



### 3、blank和null的区别

> 在Django模型字段中，`blank`和`null`有不同的含义和用途：

- `blank=True`：表示该字段在==表单==中可以为空。它主要用于**表单验证**，允许用户在表单中不填写该字段。
- `null=True`：表示该字段在==数据库==中可以存储NULL值。它主要用于**数据库层面**，允许在数据库中存储NULL值。

通常情况下，对于字符串类型的字段（如`CharField`和`TextField`），你可能会设置`blank=True`而不设置`null=True`，因为Django会将空字符串存储为`""`而不是`NULL`。对于其他类型的字段（如`IntegerField`、`DateField`等），你可能会同时设置`blank=True`和`null=True`，以允许在表单和数据库中都为空。

例如：

```python
name = models.CharField(max_length=100, blank=True)  # 表单中可以为空，数据库中存储为空字符串
description = models.TextField(blank=True, null=True)  # 表单中可以为空，数据库中存储为NULL
```
