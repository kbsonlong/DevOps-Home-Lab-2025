#!/usr/bin/env python3
"""
MCP Fetch Streamable HTTP Server

基于Model Context Protocol (MCP)的流式HTTP服务器，提供fetch和fetch_json工具。
支持JSON-RPC 2.0协议，兼容MCP Streamable HTTP传输规范。
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse

import aiohttp
from aiohttp import ClientResponseError, ClientConnectionError
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import BaseModel, Field

from .error_handler import ErrorHandler


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FetchRequest(BaseModel):
    """Fetch请求模型"""
    url: str = Field(..., description="要获取的URL")
    method: str = Field("GET", description="HTTP方法")
    headers: Optional[Dict[str, str]] = Field(None, description="请求头")
    body: Optional[str] = Field(None, description="请求体")
    timeout: Optional[int] = Field(30, description="超时时间(秒)")


class FetchJSONRequest(BaseModel):
    """Fetch JSON请求模型"""
    url: str = Field(..., description="要获取的URL")
    method: str = Field("GET", description="HTTP方法")
    headers: Optional[Dict[str, str]] = Field(None, description="请求头")
    body: Optional[str] = Field(None, description="请求体")
    timeout: Optional[int] = Field(30, description="超时时间(秒)")


class FetchMCPServer:
    """MCP Fetch Streamable HTTP服务器"""
    
    def __init__(self, server_name: str = "mcp-fetch-server"):
        """初始化MCP服务器"""
        self.server_name = server_name
        self.error_handler = ErrorHandler()
        self.session: Optional[aiohttp.ClientSession] = None
        self.mcp = Server(server_name)
        self._setup_tools()
        self._setup_handlers()
    
    def _setup_tools(self):
        """设置MCP工具"""
        
        @self.mcp.list_tools()
        async def list_tools() -> list[Tool]:
            """列出可用的工具"""
            return [
                Tool(
                    name="fetch",
                    description="获取任意URL的内容，支持各种HTTP方法和选项",
                    inputSchema=FetchRequest.model_json_schema()
                ),
                Tool(
                    name="fetch_json",
                    description="获取JSON内容并解析为结构化数据",
                    inputSchema=FetchJSONRequest.model_json_schema()
                )
            ]
        
        @self.mcp.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent | ImageContent | EmbeddedResource]:
            """调用工具"""
            if name == "fetch":
                return await self._handle_fetch(arguments)
            elif name == "fetch_json":
                return await self._handle_fetch_json(arguments)
            else:
                raise ValueError(f"未知的工具: {name}")
    
    def _setup_handlers(self):
        """设置事件处理器"""
        
        @self.mcp.list_tools()
        async def handle_list_tools():
            """处理工具列表请求"""
            self.error_handler.log_info("TOOLS", "列出可用工具")
            return {"tools": [self.fetch_tool, self.fetch_json_tool]}
        
        @self.mcp.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> dict:
            """处理工具调用请求"""
            self.error_handler.log_info("TOOLS", f"调用工具: {name}")
            
            if name == "fetch":
                return await self.fetch_tool_handler(arguments)
            elif name == "fetch_json":
                return await self.fetch_json_tool_handler(arguments)
            else:
                raise ValueError(f"未知工具: {name}")
    
    async def _ensure_session(self):
        """确保会话已创建"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=60),
                headers={"User-Agent": f"{self.server_name}/1.0.0"}
            )
    
    async def _handle_fetch(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """处理fetch工具调用"""
        try:
            request = FetchRequest(**arguments)
            
            # 验证URL
            if not self.error_handler.validate_url(request.url):
                raise ValueError(f"无效的URL: {request.url}")
            
            # 记录请求
            self.error_handler.log_request(
                method=request.method,
                url=request.url,
                client_ip="mcp-client"
            )
            
            # 检查速率限制
            if not self.error_handler.check_rate_limit("mcp-client"):
                raise ValueError("请求过于频繁，请稍后再试")
            
            # 确保会话存在
            await self._ensure_session()
            
            # 执行请求
            async with self.session.request(
                method=request.method,
                url=request.url,
                headers=request.headers or {},
                data=request.body.encode() if request.body else None,
                timeout=aiohttp.ClientTimeout(total=request.timeout or 30)
            ) as response:
                
                content = await response.text()
                
                # 构建结果
                result = {
                    "status": response.status,
                    "headers": dict(response.headers),
                    "body": content,
                    "url": str(response.url),
                    "method": request.method,
                    "size": len(content.encode('utf-8'))
                }
                
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
                
        except Exception as e:
            error_result = self.error_handler.handle_exception(e, request.url, request.method)
            return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False, indent=2))]
    
    async def _handle_fetch_json(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """处理fetch_json工具调用"""
        try:
            request = FetchJSONRequest(**arguments)
            
            # 验证URL
            if not self.error_handler.validate_url(request.url):
                raise ValueError(f"无效的URL: {request.url}")
            
            # 记录请求
            self.error_handler.log_request(
                method=request.method,
                url=request.url,
                client_ip="mcp-client"
            )
            
            # 检查速率限制
            if not self.error_handler.check_rate_limit("mcp-client"):
                raise ValueError("请求过于频繁，请稍后再试")
            
            # 确保会话存在
            await self._ensure_session()
            
            # 执行请求
            async with self.session.request(
                method=request.method,
                url=request.url,
                headers=request.headers or {},
                data=request.body.encode() if request.body else None,
                timeout=aiohttp.ClientTimeout(total=request.timeout or 30)
            ) as response:
                
                content = await response.text()
                
                # 尝试解析JSON
                try:
                    json_data = json.loads(content)
                except json.JSONDecodeError as e:
                    raise ValueError(f"响应内容不是有效的JSON: {str(e)}")
                
                # 构建结果
                result = {
                    "status": response.status,
                    "headers": dict(response.headers),
                    "body": json_data,
                    "raw_body": content,
                    "url": str(response.url),
                    "method": request.method,
                    "size": len(content.encode('utf-8'))
                }
                
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
                
        except Exception as e:
            error_result = self.error_handler.handle_exception(e, request.url, request.method)
            return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False, indent=2))]
    
    async def start(self):
        """启动服务器"""
        self.error_handler.log_info("STARTUP", "启动MCP Fetch服务器")
        await self._ensure_session()
    
    async def stop(self):
        """停止服务器"""
        self.error_handler.log_info("SHUTDOWN", "停止MCP Fetch服务器")
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def run_stdio(self):
        """运行stdio服务器"""
        await self.start()
        try:
            async with stdio_server() as (read_stream, write_stream):
                await self.mcp.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name=self.server_name,
                        server_version="1.0.0",
                        capabilities={"tools": {"listChanged": True}}
                    )
                )
        finally:
            await self.stop()


# 创建全局服务器实例
server = FetchMCPServer()


async def main():
    """主函数"""
    await server.run_stdio()


if __name__ == "__main__":
    asyncio.run(main())