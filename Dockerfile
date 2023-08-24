# 使用 Python 3.10 作为基础镜像
FROM python:3.10-slim-buster
 
# 设置工作目录
WORKDIR /app
 
# 复制应用程序代码到容器中
COPY . /app
 
# 安装依赖项
RUN pip install --no-cache-dir -r requirements.txt
 
# 暴露端口
EXPOSE 15300
 
# 启动应用程序
CMD ["python", "./bus_change/Channel/DOT_Info.py"]
