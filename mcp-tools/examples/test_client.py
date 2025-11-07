#!/usr/bin/env python3
"""
MCP Fetch Server 示例和测试

演示如何使用MCP fetch服务器进行HTTP请求
"""

import asyncio
import json
import aiohttp
from typing import Dict, Any


class MCPFetchClient:
    """MCP Fetch客户端示例"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP工具"""
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 1
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        async with self.session.post(
            f"{self.base_url}/mcp",
            json=mcp_request,
            headers=headers
        ) as response:
            result = await response.json()
            return result
    
    async def test_fetch_tool(self):
        """测试fetch工具"""
        print("=== 测试fetch工具 ===")
        
        # 测试GET请求
        print("1. 测试GET请求:")
        result = await self.call_mcp_tool("fetch", {
            "url": "https://httpbin.org/get",
            "method": "GET"
        })
        
        if "result" in result:
            content = result["result"]["content"]
            print(f"状态码: {content['status']}")
            print(f"URL: {content['url']}")
            print(f"响应体长度: {len(content['body'])} 字符")
        else:
            print(f"错误: {result}")
        
        # 测试POST请求
        print("\n2. 测试POST请求:")
        result = await self.call_mcp_tool("fetch", {
            "url": "https://httpbin.org/post",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": '{"test": "data"}'
        })
        
        if "result" in result:
            content = result["result"]["content"]
            print(f"状态码: {content['status']}")
            print(f"URL: {content['url']}")
        else:
            print(f"错误: {result}")
    
    async def test_fetch_json_tool(self):
        """测试fetch_json工具"""
        print("\n=== 测试fetch_json工具 ===")
        
        # 测试JSON API
        print("1. 测试JSON API:")
        result = await self.call_mcp_tool("fetch_json", {
            "url": "https://jsonplaceholder.typicode.com/posts/1",
            "method": "GET"
        })
        
        if "result" in result:
            content = result["result"]["content"]
            print(f"状态码: {content['status']}")
            print(f"解析的JSON: {content['body']}")
        else:
            print(f"错误: {result}")
        
        # 测试POST JSON数据
        print("\n2. 测试POST JSON数据:")
        result = await self.call_mcp_tool("fetch_json", {
            "url": "https://jsonplaceholder.typicode.com/posts",
            "method": "POST",
            "body": {
                "title": "测试标题",
                "body": "测试内容",
                "userId": 1
            }
        })
        
        if "result" in result:
            content = result["result"]["content"]
            print(f"状态码: {content['status']}")
            print(f"响应JSON: {content['body']}")
        else:
            print(f"错误: {result}")
    
    async def test_error_handling(self):
        """测试错误处理"""
        print("\n=== 测试错误处理 ===")
        
        # 测试无效URL
        print("1. 测试无效URL:")
        result = await self.call_mcp_tool("fetch", {
            "url": "not-a-valid-url",
            "method": "GET"
        })
        print(f"结果: {result}")
        
        # 测试超时
        print("\n2. 测试超时:")
        result = await self.call_mcp_tool("fetch", {
            "url": "https://httpbin.org/delay/35",
            "method": "GET",
            "timeout": 5
        })
        print(f"结果: {result}")
    
    async def test_streamable_http(self):
        """测试Streamable HTTP传输"""
        print("\n=== 测试Streamable HTTP传输 ===")
        
        # 测试SSE流式响应
        print("1. 测试SSE流式响应:")
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "fetch",
                "arguments": {
                    "url": "https://httpbin.org/get",
                    "method": "GET"
                }
            },
            "id": 1
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        
        async with self.session.post(
            f"{self.base_url}/mcp",
            json=mcp_request,
            headers=headers
        ) as response:
            print(f"响应头: {dict(response.headers)}")
            
            # 读取SSE响应
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    print(f"SSE数据: {data}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        print(f"开始测试MCP Fetch服务器: {self.base_url}")
        print("=" * 50)
        
        try:
            # 检查服务器是否运行
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    health_info = await response.json()
                    print(f"服务器状态: {health_info}")
                else:
                    print(f"服务器未响应: {response.status}")
                    return
            
            # 运行测试
            await self.test_fetch_tool()
            await self.test_fetch_json_tool()
            await self.test_error_handling()
            await self.test_streamable_http()
            
            print("\n" + "=" * 50)
            print("所有测试完成！")
            
        except Exception as e:
            print(f"测试失败: {e}")


async def main():
    """主函数"""
    async with MCPFetchClient() as client:
        await client.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())