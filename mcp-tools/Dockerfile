FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY pyproject.toml ./
COPY mcp_fetch_server/ ./mcp_fetch_server/
COPY examples/ ./examples/
COPY tests/ ./tests/

# 安装Python依赖
RUN pip install --no-cache-dir -e .

# 创建非root用户
RUN useradd -m -u 1000 mcp && chown -R mcp:mcp /app
USER mcp

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["python", "-m", "mcp_fetch_server.http_transport", "--host", "0.0.0.0", "--port", "8000"]