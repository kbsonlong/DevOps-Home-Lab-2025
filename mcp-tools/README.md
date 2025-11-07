# MCP Fetch Streamable HTTP Server

基于Model Context Protocol (MCP)的流式HTTP服务器，提供fetch和fetch_json工具，支持JSON-RPC 2.0协议和MCP Streamable HTTP传输规范。

## 🌟 特性

- **MCP协议支持**: 完整的MCP服务器实现，支持工具调用
- **流式HTTP传输**: 支持标准HTTP和Server-Sent Events (SSE)
- **强大的fetch工具**: 支持GET、POST、PUT、DELETE等HTTP方法
- **JSON解析**: 自动解析和验证JSON响应
- **错误处理**: 全面的错误处理和日志记录
- **速率限制**: 内置请求速率限制保护
- **Web界面**: 提供友好的Web管理界面
- **CORS支持**: 跨域请求支持
- **Docker支持**: 容器化部署

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd mcp-fetch-server

# 安装依赖
pip install -e .

# 或者使用Poetry
poetry install
```

### 运行服务器

#### 方式1: HTTP传输模式 (推荐)
```bash
# 启动HTTP服务器
python -m mcp_fetch_server.http_transport --host 0.0.0.0 --port 8000

# 使用自定义配置
python -m mcp_fetch_server.http_transport --host 0.0.0.0 --port 8080 --name my-fetch-server
```

#### 方式2: stdio传输模式
```bash
# 启动stdio服务器
python -m mcp_fetch_server.server
```

### Docker运行

```bash
# 构建镜像
docker build -t mcp-fetch-server .

# 运行容器
docker run -p 8000:8000 mcp-fetch-server
```

## 📋 API文档

### 端点

- `GET /` - Web管理界面
- `GET /health` - 健康检查
- `GET /info` - 服务器信息
- `GET /tools` - 列出可用工具
- `POST /tools/{tool_name}` - 调用工具
- `POST /mcp` - MCP Streamable HTTP端点

### 工具

#### fetch工具
获取任意URL的内容，支持各种HTTP方法。

**参数:**
- `url` (string, 必需): 要获取的URL
- `method` (string, 可选): HTTP方法，默认为"GET"
- `headers` (object, 可选): 请求头字典
- `body` (string, 可选): 请求体
- `timeout` (integer, 可选): 超时时间(秒)，默认为30

**返回:**
```json
{
  "status": 200,
  "headers": {...},
  "body": "响应内容",
  "url": "最终URL",
  "method": "GET",
  "size": 1024
}
```

#### fetch_json工具
获取JSON内容并解析为结构化数据。

**参数:**
- `url` (string, 必需): 要获取的URL
- `method` (string, 可选): HTTP方法，默认为"GET"
- `headers` (object, 可选): 请求头字典
- `body` (string, 可选): 请求体
- `timeout` (integer, 可选): 超时时间(秒)，默认为30

**返回:**
```json
{
  "status": 200,
  "headers": {...},
  "body": {...},
  "raw_body": "原始JSON字符串",
  "url": "最终URL",
  "method": "GET",
  "size": 512
}
```

## 💻 使用示例

### 使用fetch工具

```bash
# 获取网页内容
curl -X POST http://localhost:8000/tools/fetch \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {
      "url": "https://example.com",
      "method": "GET"
    }
  }'

# POST请求
curl -X POST http://localhost:8000/tools/fetch \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {
      "url": "https://api.example.com/users",
      "method": "POST",
      "headers": {"Content-Type": "application/json"},
      "body": "{\\"name\\": \\"John Doe\\", \\"email\\": \\"john@example.com\\"}"
    }
  }'
```

### 使用fetch_json工具

```bash
# 获取JSON API数据
curl -X POST http://localhost:8000/tools/fetch_json \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {
      "url": "https://api.github.com/users/octocat",
      "method": "GET"
    }
  }'
```

### 使用MCP协议

```bash
# 列出可用工具
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
  }'

# 调用工具
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "fetch",
      "arguments": {"url": "https://example.com"}
    },
    "id": 2
  }'
```

### 使用Server-Sent Events (SSE)

```bash
# SSE流式响应
curl -N http://localhost:8000/mcp \
  -H "Accept: text/event-stream" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "fetch",
      "arguments": {"url": "https://example.com"}
    },
    "id": 1
  }'
```

## 🔧 配置

### 环境变量

- `MCP_SERVER_NAME`: 服务器名称 (默认: "mcp-fetch-server")
- `MCP_SERVER_HOST`: 监听主机 (默认: "127.0.0.1")
- `MCP_SERVER_PORT`: 监听端口 (默认: 8000)
- `MCP_LOG_LEVEL`: 日志级别 (默认: "INFO")
- `MCP_RATE_LIMIT`: 速率限制 (默认: 100)
- `MCP_TIMEOUT`: 默认超时时间 (默认: 30)

### 命令行参数

```bash
python -m mcp_fetch_server.http_transport --help

选项:
  --host HOST          主机地址 (默认: 127.0.0.1)
  --port PORT          端口 (默认: 8000)
  --name NAME          服务器名称 (默认: mcp-fetch-server)
  --log-level LEVEL    日志级别 (默认: INFO)
```

## 🧪 测试

运行测试套件:

```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_server.py
pytest tests/test_error_handler.py

# 带覆盖率测试
pytest --cov=mcp_fetch_server tests/
```

## 🐳 Docker部署

### 构建镜像

```bash
docker build -t mcp-fetch-server .
```

### 运行容器

```bash
# 基本运行
docker run -d -p 8000:8000 --name mcp-fetch mcp-fetch-server

# 自定义配置
docker run -d -p 8080:8000 \
  -e MCP_SERVER_NAME=my-server \
  -e MCP_LOG_LEVEL=DEBUG \
  --name mcp-fetch \
  mcp-fetch-server

# 使用docker-compose
docker-compose up -d
```

### docker-compose.yml示例

```yaml
version: '3.8'

services:
  mcp-fetch-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MCP_SERVER_NAME=mcp-fetch-server
      - MCP_LOG_LEVEL=INFO
      - MCP_RATE_LIMIT=100
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 🔒 安全特性

- **URL验证**: 防止访问恶意URL
- **速率限制**: 内置请求频率限制
- **CORS保护**: 跨域请求控制
- **超时保护**: 防止长时间运行的请求
- **错误处理**: 安全的错误信息返回
- **日志记录**: 完整的请求和错误日志

## 📊 监控和日志

### 日志格式

```
2024-01-20 10:30:45,123 - mcp_fetch_server - INFO - 启动MCP Fetch服务器
2024-01-20 10:30:45,456 - mcp_fetch_server - INFO - 处理请求: GET https://api.example.com/data
2024-01-20 10:30:45,789 - mcp_fetch_server - INFO - 请求成功: 200 OK (1024 bytes)
```

### 健康检查

```bash
# 检查服务器状态
curl http://localhost:8000/health

# 获取服务器信息
curl http://localhost:8000/info
```

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

### 开发环境

```bash
# 克隆项目
git clone <repository-url>
cd mcp-fetch-server

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black mcp_fetch_server/
isort mcp_fetch_server/

# 类型检查
mypy mcp_fetch_server/
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP协议规范
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Web框架
- [aiohttp](https://docs.aiohttp.org/) - 异步HTTP客户端
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - MCP Python实现

## 📞 支持

如果你遇到问题或有建议，请通过以下方式联系我们:

- 提交GitHub Issue
- 查看文档和示例
- 参与社区讨论

---

**Happy coding! 🚀**
