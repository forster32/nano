FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录文件到工作目录
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置默认命令
CMD ["bash"]