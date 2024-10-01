"""
OAback 项目的 URL 配置.

`urlpatterns` 列表将 URL 路由映射到视图.更多信息请参见：
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
示例：
函数视图
    1. 添加导入：from my_app import views
    2. 向 urlpatterns 添加 URL：path('', views.home, name='home')
基于类的视图
    1. 添加导入：from other_app.views import Home
    2. 向 urlpatterns 添加 URL：path('', Home.as_view(), name='home')
包括另一个 URLconf
    1. 导入 include() 函数：from django.urls import include, path
    2. 向 urlpatterns 添加 URL：path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('auth/', include('apps.oaauth.urls')),
    path('absent/', include('apps.absent.urls')),
    path('inform/', include('apps.inform.urls')),
    path('staff/', include('apps.staff.urls')),
    path('image/', include('apps.image.urls')),
]
