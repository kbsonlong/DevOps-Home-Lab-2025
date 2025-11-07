#!/usr/bin/env python3
"""
MCP Fetch Streamable HTTP Server - FastAPI HTTP Transport

基于FastAPI的MCP Streamable HTTP服务器实现，支持Web界面和API端点。
"""

import asyncio
import json
import logging
import signal
import sys
from typing import Any, Dict, Optional

import aiohttp
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel

from mcp_fetch_server.server import FetchMCPServer
from mcp_fetch_server.error_handler import ErrorHandler


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HTTPTransportServer:
    """MCP Streamable HTTP传输服务器"""
    
    def __init__(self, server_name: str = "mcp-fetch-server"):
        self.server_name = server_name
        self.mcp_server = FetchMCPServer(server_name)
        self.error_handler = ErrorHandler()
        self.app = FastAPI(
            title=server_name,
            description="MCP Fetch Streamable HTTP Server",
            version="1.0.0"
        )
        self._setup_routes()
        self._setup_middleware()
        self.running = False
    
    def _setup_routes(self):
        """设置HTTP路由"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def root():
            """根路径 - 提供Web界面"""
            return self._get_web_interface()
        
        @self.app.get("/health")
        async def health():
            """健康检查端点"""
            return {
                "status": "healthy",
                "server": self.server_name,
                "timestamp": asyncio.get_event_loop().time()
            }
        
        @self.app.get("/info")
        async def info():
            """服务器信息"""
            return {
                "name": self.server_name,
                "version": "1.0.0",
                "transport": "streamable-http",
                "endpoints": {
                    "mcp": "/mcp",
                    "health": "/health",
                    "info": "/info",
                    "docs": "/docs"
                },
                "tools": ["fetch", "fetch_json"]
            }
        
        @self.app.post("/mcp")
        async def mcp_endpoint(request: Request):
            """MCP Streamable HTTP端点"""
            try:
                # 获取客户端IP
                client_ip = self.error_handler.get_client_ip(request)
                
                # 获取请求体
                body = await request.json()
                
                # 记录请求
                self.error_handler.log_request(
                    method="POST",
                    url="/mcp",
                    client_ip=client_ip,
                    user_agent=request.headers.get("user-agent", "")
                )
                
                # 处理MCP消息
                response = await self.mcp_server.mcp.handle_message(body)
                
                # 检查是否需要流式响应
                accept_header = request.headers.get("accept", "")
                if "text/event-stream" in accept_header:
                    # 返回SSE流式响应
                    async def event_stream():
                        yield f"data: {json.dumps(response)}\n\n"
                    
                    return StreamingResponse(
                        event_stream(),
                        media_type="text/event-stream",
                        headers=self._get_cors_headers()
                    )
                else:
                    # 返回JSON响应
                    return Response(
                        content=json.dumps(response),
                        media_type="application/json",
                        headers=self._get_cors_headers()
                    )
                    
            except Exception as e:
                self.error_handler.log_error(
                    "ERROR",
                    f"MCP处理错误: {str(e)}",
                    {
                        "url": "/mcp",
                        "method": "POST",
                        "client_ip": client_ip
                    }
                )
                
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": str(e)
                    },
                    "id": None
                }
                return Response(
                    content=json.dumps(error_response),
                    media_type="application/json",
                    status_code=500,
                    headers=self._get_cors_headers()
                )
        
        @self.app.options("/mcp")
        async def mcp_options():
            """CORS预检请求处理"""
            return Response(
                content="",
                headers=self._get_cors_headers()
            )
        
        @self.app.get("/tools")
        async def list_tools():
            """列出可用工具"""
            try:
                tools = await self.mcp_server.mcp.list_tools()
                return {
                    "tools": [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "inputSchema": tool.inputSchema
                        }
                        for tool in tools
                    ]
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/tools/{tool_name}")
        async def call_tool(tool_name: str, request: Request):
            """调用工具"""
            try:
                body = await request.json()
                arguments = body.get("arguments", {})
                
                # 调用MCP工具
                result = await self.mcp_server.mcp.call_tool(tool_name, arguments)
                
                return {
                    "result": result,
                    "tool": tool_name,
                    "arguments": arguments
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    def _setup_middleware(self):
        """设置中间件"""
        
        @self.app.middleware("http")
        async def add_process_time_header(request: Request, call_next):
            """添加处理时间头部"""
            start_time = asyncio.get_event_loop().time()
            response = await call_next(request)
            process_time = asyncio.get_event_loop().time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            return response
    
    def _get_cors_headers(self) -> Dict[str, str]:
        """获取CORS头部"""
        return {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Accept, Authorization",
            "Access-Control-Max-Age": "86400"
        }
    
    def _get_web_interface(self) -> str:
        """获取Web界面HTML"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Fetch Server</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .endpoint {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 4px solid #3498db;
        }
        .tool {
            background: #e8f5e8;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 4px solid #27ae60;
        }
        code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        pre {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
        .status {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 3px;
            font-weight: bold;
        }
        .status.running {
            background: #27ae60;
            color: white;
        }
        button {
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background: #2980b9;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 MCP Fetch Streamable HTTP Server</h1>
        
        <div class="status running">服务器运行中</div>
        
        <h2>📋 服务器信息</h2>
        <div class="endpoint">
            <strong>服务器名称:</strong> {server_name}<br>
            <strong>传输协议:</strong> Streamable HTTP<br>
            <strong>版本:</strong> 1.0.0
        </div>
        
        <h2>🔧 可用工具</h2>
        
        <div class="tool">
            <h3>fetch</h3>
            <p>获取任意URL的内容，支持各种HTTP方法和选项</p>
            <strong>参数:</strong>
            <ul>
                <li><code>url</code> - 要获取的URL (必需)</li>
                <li><code>method</code> - HTTP方法，默认为GET</li>
                <li><code>headers</code> - 请求头字典</li>
                <li><code>body</code> - 请求体</li>
                <li><code>timeout</code> - 超时时间(秒)，默认为30</li>
            </ul>
        </div>
        
        <div class="tool">
            <h3>fetch_json</h3>
            <p>获取JSON内容并解析为结构化数据</p>
            <strong>参数:</strong>
            <ul>
                <li><code>url</code> - 要获取的URL (必需)</li>
                <li><code>method</code> - HTTP方法，默认为GET</li>
                <li><code>headers</code> - 请求头字典</li>
                <li><code>body</code> - 请求体</li>
                <li><code>timeout</code> - 超时时间(秒)，默认为30</li>
            </ul>
        </div>
        
        <h2>🌐 API端点</h2>
        
        <div class="endpoint">
            <strong>GET /</strong> - 此Web界面
        </div>
        
        <div class="endpoint">
            <strong>GET /health</strong> - 健康检查
        </div>
        
        <div class="endpoint">
            <strong>GET /info</strong> - 服务器信息
        </div>
        
        <div class="endpoint">
            <strong>GET /tools</strong> - 列出可用工具
        </div>
        
        <div class="endpoint">
            <strong>POST /tools/{tool_name}</strong> - 调用工具
        </div>
        
        <div class="endpoint">
            <strong>POST /mcp</strong> - MCP Streamable HTTP端点
        </div>
        
        <h2>🚀 快速测试</h2>
        
        <button onclick="testHealth()">测试健康状态</button>
        <button onclick="testTools()">测试工具列表</button>
        <button onclick="testFetch()">测试fetch工具</button>
        
        <div id="result" style="margin-top: 20px;"></div>
        
        <h2>📚 使用示例</h2>
        
        <h3>使用fetch工具:</h3>
        <pre>
curl -X POST http://localhost:8000/tools/fetch \\\n  -H "Content-Type: application/json" \\\n  -d '{
    "arguments": {
      "url": "https://api.github.com/users/octocat",
      "method": "GET"
    }
  }'
        </pre>
        
        <h3>使用MCP协议:</h3>
        <pre>
curl -X POST http://localhost:8000/mcp \\\n  -H "Content-Type: application/json" \\\n  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
  }'
        </pre>
        
        <h3>使用Server-Sent Events:</h3>
        <pre>
curl -N http://localhost:8000/mcp \\\n  -H "Accept: text/event-stream" \\\n  -X POST \\\n  -H "Content-Type: application/json" \\\n  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "fetch",
      "arguments": {"url": "https://example.com"}
    },
    "id": 1
  }'
        </pre>
    </div>
    
    <script>
        function displayResult(data) {
            document.getElementById('result').innerHTML = 
                '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
        }
        
        async function testHealth() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                displayResult(data);
            } catch (error) {
                displayResult({error: error.message});
            }
        }
        
        async function testTools() {
            try {
                const response = await fetch('/tools');
                const data = await response.json();
                displayResult(data);
            } catch (error) {
                displayResult({error: error.message});
            }
        }
        
        async function testFetch() {
            try {
                const response = await fetch('/tools/fetch', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        arguments: {
                            url: 'https://httpbin.org/json',
                            method: 'GET'
                        }
                    })
                });
                const data = await response.json();
                displayResult(data);
            } catch (error) {
                displayResult({error: error.message});
            }
        }
    </script>
</body>
</html>
        """.format(server_name=self.server_name)
    
    async def start(self, host: str = "127.0.0.1", port: int = 8000):
        """启动HTTP服务器"""
        self.host = host
        self.port = port
        self.error_handler.log_info("STARTUP", f"启动HTTP传输服务器: {host}:{port}")
        await self.mcp_server.start()
        self.running = True
        
        import uvicorn
        config = uvicorn.Config(
            self.app,
            host=host,
            port=port,
            log_level="info"
        )
        self.server = uvicorn.Server(config)
        
        # 设置信号处理
        def signal_handler(signum, frame):
            self.error_handler.log_info("SIGNAL", f"接收到信号 {signum}，正在关闭服务器...")
            self.running = False
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            await self.server.serve()
        except KeyboardInterrupt:
            self.error_handler.log_info("SHUTDOWN", "服务器被用户中断")
        finally:
            await self.stop()
    
    async def stop(self):
        """停止HTTP服务器"""
        if self.running:
            self.error_handler.log_info("SHUTDOWN", "停止HTTP传输服务器")
            self.running = False
            await self.mcp_server.stop()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Fetch Streamable HTTP Server")
    parser.add_argument("--host", default="127.0.0.1", help="主机地址 (默认: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="端口 (默认: 8000)")
    parser.add_argument("--name", default="mcp-fetch-server", help="服务器名称")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="日志级别")
    
    args = parser.parse_args()
    
    # 设置日志级别
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # 创建并运行服务器
    server = HTTPTransportServer(args.name)
    
    server.error_handler.log_info("MAIN", f"启动MCP Fetch Streamable HTTP服务器...")
    server.error_handler.log_info("MAIN", f"服务器名称: {args.name}")
    server.error_handler.log_info("MAIN", f"地址: http://{args.host}:{args.port}")
    server.error_handler.log_info("MAIN", f"Web界面: http://{args.host}:{args.port}/")
    server.error_handler.log_info("MAIN", f"健康检查: http://{args.host}:{args.port}/health")
    server.error_handler.log_info("MAIN", f"MCP端点: http://{args.host}:{args.port}/mcp")
    
    try:
        asyncio.run(server.start(args.host, args.port))
    except KeyboardInterrupt:
        server.error_handler.log_info("MAIN", "服务器被用户中断")
    except Exception as e:
            server.error_handler.log_error("ERROR", f"服务器运行错误: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()