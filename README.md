[toc]

# OAback

> 基于 `Django `框架开发的OA系统.

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

