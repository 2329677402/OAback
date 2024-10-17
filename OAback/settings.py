"""
OAback 项目的 Django 设置。

由“django-admin startproject”使用 Django 5.1.1 生成。

有关此文件的更多信息，请参阅
https://docs.djangoproject.com/en/5.1/topics/settings/

有关设置及其值的完整列表，请参阅
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
import environ

# 读取.env文件, 方便管理和区分开发环境和生产环境的配置
env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent
# 读取.env文件，在服务器项目的根路径上要创建一个
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# 从 django.contrib.auth.models 导入用户

# 在项目内部构建路径，如下所示：BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# 快速启动开发设置 - 不适合生产
# 请参阅 https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# 安全警告：对生产中使用的密钥保密！
SECRET_KEY = 'django-insecure-vq@_n*hy*)@bs443bt4x@sld#mr-0k#e!q^(gj7hs!%t&0@rtg'

# 安全警告：请勿在生产环境中开启调试运行!
DEBUG = True

# 允许访问的主机, * 代表所有主机, 设置具体的域名或IP地址, 则只允许该域名或IP访问
ALLOWED_HOSTS = ['*']

# 应用程序定义

# 使用 `"apps.image.apps.ImageConfig"` 和 `"apps.image"` 在 `INSTALLED_APPS` 中的结果是一样的.
# 两者都会安装 `apps.image` 应用程序，只是前者显式地指定了配置类，而后者依赖于 Django 的默认查找机制.
INSTALLED_APPS = [
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    # 'django.contrib.sessions',
    # 'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # 安装rest_framework
    'corsheaders',  # 安装跨域中间件
    'apps.oaauth.apps.OaauthConfig',  # 安装用户app
    'apps.absent.apps.AbsentConfig',  # 安装考勤app
    "apps.inform.apps.InformConfig",  # 安装通知app
    "apps.staff.apps.StaffConfig",  # 安装员工app
    "apps.image.apps.ImageConfig",  # 上传图片app
    "apps.home.apps.HomeConfig"  # 首页app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'django.contrib.sessions.middleware.SessionMiddleware',
    # 跨域中间件, 一定要放在CommonMiddleware之前
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 前端通过Vue去渲染，不再使用Django的模板，并且使用JWT进行认证，不是通过cookie，无需开启csrf保护
    # 'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.oaauth.middleware.LoginCheckMiddleware',  # 注册中间件
]

ROOT_URLCONF = 'OAback.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                # 'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'OAback.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        "NAME": env.str('DB_NAME', 'djangoa'),
        "USER": env.str('DB_USER', "root"),
        "PASSWORD": env.str("DB_PASSWORD", "123456"),
        "HOST": env.str('DB_HOST', 'localhost'),
        "PORT": env.str('DB_PORT', 3306),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

# 语言及时区设置
LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'  # 静态文件访问路径
STATICFILES_DIRS = [BASE_DIR / 'static']  # 静态文件读取目录

MEDIA_ROOT = BASE_DIR / 'media'  # 媒体文件路径
MEDIA_URL = '/media/'  # 媒体文件访问路径

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 允许所有域名跨域访问
CORS_ALLOW_ALL_ORIGINS = True

# 覆盖Django的User模型
# AUTH_USER_MODEL = 'apps.oaauth.models.OAUser'写法是不对的
# 正确写法是AUTH_USER_MODEL = 'app名称.User模型类名'
AUTH_USER_MODEL = 'oaauth.OAUser'

# 配置REST_FRAMEWORK参数
REST_FRAMEWORK = {
    # 配置默认鉴权方式--JWT
    'DEFAULT_AUTHENTICATION_CLASSES': ['apps.oaauth.authentications.UserTokenAuthentication'],
    # 配置默认分页器, 全局分页
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

APPEND_SLASH = False  # 关闭Django的url末尾添加 "/" 功能

# 发送QQ邮件设置
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_SSL = True  # 使用SSL加密
EMAIL_HOST = "smtp.qq.com"  # QQ邮箱的SMTP服务器地址
EMAIL_PORT = 465  # QQ邮箱的SMTP服务器端口号
EMAIL_HOST_USER = "3157043973@qq.com"  # 发送邮件的QQ邮箱账号
EMAIL_HOST_PASSWORD = "cjczahqenepjddhh"  # QQ邮箱的授权码
DEFAULT_FROM_EMAIL = "3157043973@qq.com"  # 默认发件人

# Celery配置, 用于异步任务
# 中间人的配置
CELERY_BROKER_URL = env.str('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/1')
# 指定结果的接受地址
CELERY_RESULT_BACKEND = env.str('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/2')
# 任务序列化和反序列化使用msgpack方案
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# 缓存配置
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env.str('CACHE_URL', "redis://127.0.0.1:6379/3"),
    }
}

# 日志配置
LOGGING = {
    "version": 1,
    'disable_existing_loggers': True,
    # 输出日志格式
    'formatters': {
        # 详细的日志格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        # 简单的日志格式
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    # 过滤器
    'handlers': {
        # 控制台输出信息
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        # 日志文件位置
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/data/log/oa.log',
            'formatter': 'verbose'
        },
    },
    # 日志处理器
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    },
}
