# 使用官方 Python 运行时作为父镜像
FROM python:3.7.7

# 在容器中设置工作目录
WORKDIR /Seal_system

# 将 requirements 文件复制到容器的 /Seal_system 目录
COPY requirements.txt ./

# 安装 requirements.txt 中指定的依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装系统依赖，包括 ping 和 ffmpeg
RUN apt-get update && apt-get install -y iputils-ping ffmpeg vim

# 将当前目录内容复制到容器的 /Seal_system 目录
COPY . .

# 设置环境变量
ENV LANG C.UTF-8

# 设置时区为中国标准时间
ENV TZ=Asia/Shanghai

# 安装 Nginx
RUN apt-get install -y nginx

# 复制 Nginx 配置文件
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露 Gunicorn 将运行的端口
EXPOSE 5000

# 启动 Nginx 和 Gunicorn
CMD service nginx start && gunicorn main:app -b 0.0.0.0:5000 -w 3




