import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch
from mcp_fetch_server.server import FetchMCPServer


@pytest.fixture
async def server():
    """创建测试服务器实例"""
    server = FetchMCPServer("test-server")
    yield server
    await server.stop()


@pytest.fixture
async def client_session():
    """创建测试客户端会话"""
    import aiohttp
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.mark.asyncio
async def test_fetch_tool_get_request(server):
    """测试fetch工具的GET请求"""
    # 模拟aiohttp响应
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"content-type": "text/html"}
    mock_response.text = AsyncMock(return_value="<html>test</html>")
    mock_response.url = "https://example.com"
    
    # 模拟会话和请求
    mock_session = AsyncMock()
    mock_session.request = AsyncMock(return_value=mock_response)
    
    server.session = mock_session
    
    # 调用fetch工具
    result = await server.mcp.tools["fetch"].function(
        url="https://example.com",
        method="GET"
    )
    
    # 验证结果
    assert result["status"] == 200
    assert result["body"] == "<html>test</html>"
    assert result["url"] == "https://example.com"
    assert result["method"] == "GET"


@pytest.mark.asyncio
async def test_fetch_tool_post_request(server):
    """测试fetch工具的POST请求"""
    # 模拟aiohttp响应
    mock_response = AsyncMock()
    mock_response.status = 201
    mock_response.headers = {"content-type": "application/json"}
    mock_response.text = AsyncMock(return_value='{"id": 123}')
    mock_response.url = "https://api.example.com/items"
    
    # 模拟会话和请求
    mock_session = AsyncMock()
    mock_session.request = AsyncMock(return_value=mock_response)
    
    server.session = mock_session
    
    # 调用fetch工具
    result = await server.mcp.tools["fetch"].function(
        url="https://api.example.com/items",
        method="POST",
        headers={"Content-Type": "application/json"},
        body='{"name": "test"}'
    )
    
    # 验证结果
    assert result["status"] == 201
    assert result["body"] == '{"id": 123}'
    assert result["url"] == "https://api.example.com/items"
    assert result["method"] == "POST"


@pytest.mark.asyncio
async def test_fetch_json_tool(server):
    """测试fetch_json工具"""
    # 模拟aiohttp响应
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"content-type": "application/json"}
    mock_response.text = AsyncMock(return_value='{"user": {"id": 1, "name": "test"}}')
    mock_response.url = "https://api.example.com/user/1"
    
    # 模拟会话和请求
    mock_session = AsyncMock()
    mock_session.request = AsyncMock(return_value=mock_response)
    
    server.session = mock_session
    
    # 调用fetch_json工具
    result = await server.mcp.tools["fetch_json"].function(
        url="https://api.example.com/user/1",
        method="GET"
    )
    
    # 验证结果
    assert result["status"] == 200
    assert result["body"]["user"]["id"] == 1
    assert result["body"]["user"]["name"] == "test"
    assert result["raw_body"] == '{"user": {"id": 1, "name": "test"}}'


@pytest.mark.asyncio
async def test_invalid_url(server):
    """测试无效URL"""
    # 调用fetch工具使用无效URL
    with pytest.raises(ValueError, match="Invalid URL"):
        await server.mcp.tools["fetch"].function(
            url="not-a-valid-url",
            method="GET"
        )


@pytest.mark.asyncio
async def test_timeout_error(server):
    """测试超时错误"""
    # 模拟超时异常
    mock_session = AsyncMock()
    mock_session.request = AsyncMock(side_effect=asyncio.TimeoutError())
    
    server.session = mock_session
    
    # 调用fetch工具应该抛出超时异常
    with pytest.raises(HTTPException) as exc_info:
        await server.mcp.tools["fetch"].function(
            url="https://example.com",
            method="GET",
            timeout=5
        )
    
    assert "Request timeout" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_server_health_endpoint(server):
    """测试服务器健康检查端点"""
    from fastapi.testclient import TestClient
    
    client = TestClient(server.get_app())
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["server"] == "test-server"


@pytest.mark.asyncio
async def test_server_root_endpoint(server):
    """测试服务器根端点"""
    from fastapi.testclient import TestClient
    
    client = TestClient(server.get_app())
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-server"
    assert data["transport"] == "streamable-http"
    assert "mcp" in data["endpoints"]


@pytest.mark.asyncio
async def test_mcp_endpoint(server):
    """测试MCP端点"""
    from fastapi.testclient import TestClient
    
    client = TestClient(server.get_app())
    
    # 创建MCP请求
    mcp_request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 1
    }
    
    response = client.post("/mcp", json=mcp_request)
    
    assert response.status_code == 200
    data = response.json()
    assert "jsonrpc" in data
    assert data["jsonrpc"] == "2.0"


@pytest.mark.asyncio
async def test_cors_headers(server):
    """测试CORS头"""
    from fastapi.testclient import TestClient
    
    client = TestClient(server.get_app())
    response = client.options("/mcp")
    
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers


if __name__ == "__main__":
    pytest.main([__file__])