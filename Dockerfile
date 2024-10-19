#### 第一部分. 构建镜像时执行的操作
# 基础镜像
FROM python:3.12.4

# 将当前目录下的所有文件拷贝到镜像的/www/目录下
COPY . /www/

# 将工作目录切换到/www/下
WORKDIR /www

# 安装依赖
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 安装uwsgi
RUN pip install uwsgi==2.0.25.1 -i https://pypi.tuna.tsinghua.edu.cn/simple

# 创建log和sock目录
RUN mkdir -p /data/log
RUN mkdir -p /data/sock

# 暴露端口
EXPOSE 8000

#### 第二部分. ENTRYPOINT: 运行容器时执行的操作
ENTRYPOINT python manage.py migrate; \
python manage.py initdepartments; \
python manage.py inituser; \
python manage.py initabsenttype; \
celery -A oaback worker -l INFO --detach; \
uwsgi --ini uwsgi.ini