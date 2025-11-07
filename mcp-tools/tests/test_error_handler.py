import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from mcp_fetch_server.error_handler import ErrorHandler


@pytest.fixture
def error_handler():
    """创建错误处理器实例"""
    return ErrorHandler("test-server")


def test_error_handler_initialization(error_handler):
    """测试错误处理器初始化"""
    assert error_handler.server_name == "test-server"
    assert error_handler.logger is not None


def test_log_request(error_handler):
    """测试请求日志记录"""
    with patch.object(error_handler.logger, 'info') as mock_info:
        error_handler.log_request(
            method="GET",
            url="https://example.com",
            client_ip="127.0.0.1",
            user_agent="test-agent"
        )
        mock_info.assert_called_once()


def test_log_error(error_handler):
    """测试错误日志记录"""
    with patch.object(error_handler.logger, 'error') as mock_error:
        error_handler.log_error(
            error="Test error",
            url="https://example.com",
            method="GET",
            client_ip="127.0.0.1"
        )
        mock_error.assert_called_once()


def test_log_warning(error_handler):
    """测试警告日志记录"""
    with patch.object(error_handler.logger, 'warning') as mock_warning:
        error_handler.log_warning(
            message="Test warning",
            url="https://example.com",
            method="GET"
        )
        mock_warning.assert_called_once()


def test_log_info(error_handler):
    """测试信息日志记录"""
    with patch.object(error_handler.logger, 'info') as mock_info:
        error_handler.log_info("Test info message")
        mock_info.assert_called_once()


def test_log_debug(error_handler):
    """测试调试日志记录"""
    with patch.object(error_handler.logger, 'debug') as mock_debug:
        error_handler.log_debug("Test debug message")
        mock_debug.assert_called_once()


def test_handle_exception_http_error(error_handler):
    """测试HTTP异常处理"""
    from aiohttp import ClientResponseError
    
    exception = ClientResponseError(
        request_info=None,
        history=None,
        status=404
    )
    
    result = error_handler.handle_exception(exception, "https://example.com", "GET")
    
    assert result["error"]["type"] == "http_error"
    assert result["error"]["status_code"] == 404
    assert "message" in result["error"]


def test_handle_exception_timeout(error_handler):
    """测试超时异常处理"""
    exception = asyncio.TimeoutError()
    
    result = error_handler.handle_exception(exception, "https://example.com", "GET")
    
    assert result["error"]["type"] == "timeout"
    assert "message" in result["error"]


def test_handle_exception_connection(error_handler):
    """测试连接异常处理"""
    from aiohttp import ClientConnectionError
    
    exception = ClientConnectionError("Connection failed")
    
    result = error_handler.handle_exception(exception, "https://example.com", "GET")
    
    assert result["error"]["type"] == "connection_error"
    assert "message" in result["error"]


def test_handle_exception_json_decode(error_handler):
    """测试JSON解码异常处理"""
    import json
    
    exception = json.JSONDecodeError("Invalid JSON", "test", 0)
    
    result = error_handler.handle_exception(exception, "https://example.com", "GET")
    
    assert result["error"]["type"] == "json_decode_error"
    assert "message" in result["error"]


def test_handle_exception_generic(error_handler):
    """测试通用异常处理"""
    exception = ValueError("Test error")
    
    result = error_handler.handle_exception(exception, "https://example.com", "GET")
    
    assert result["error"]["type"] == "internal_error"
    assert "message" in result["error"]


def test_validate_url_valid(error_handler):
    """测试有效URL验证"""
    valid_urls = [
        "https://example.com",
        "http://localhost:8080",
        "https://api.example.com/v1/users",
        "http://192.168.1.1:3000"
    ]
    
    for url in valid_urls:
        assert error_handler.validate_url(url) is True


def test_validate_url_invalid(error_handler):
    """测试无效URL验证"""
    invalid_urls = [
        "not-a-url",
        "ftp://example.com",
        "javascript:alert(1)",
        "file:///etc/passwd",
        ""
    ]
    
    for url in invalid_urls:
        assert error_handler.validate_url(url) is False


def test_sanitize_headers(error_handler):
    """测试头信息清理"""
    headers = {
        "User-Agent": "test-agent",
        "Authorization": "Bearer secret-token",
        "X-API-Key": "secret-key",
        "Content-Type": "application/json"
    }
    
    sanitized = error_handler.sanitize_headers(headers)
    
    assert sanitized["User-Agent"] == "test-agent"
    assert sanitized["Authorization"] == "[REDACTED]"
    assert sanitized["X-API-Key"] == "[REDACTED]"
    assert sanitized["Content-Type"] == "application/json"


def test_check_rate_limit(error_handler):
    """测试速率限制检查"""
    client_ip = "127.0.0.1"
    
    # 第一次请求应该允许
    assert error_handler.check_rate_limit(client_ip) is True
    
    # 多次请求应该触发速率限制
    for _ in range(10):
        error_handler.check_rate_limit(client_ip)
    
    # 应该触发速率限制
    assert error_handler.check_rate_limit(client_ip) is False


def test_get_client_ip(error_handler):
    """测试客户端IP获取"""
    # 模拟请求对象
    mock_request = AsyncMock()
    mock_request.client.host = "192.168.1.1"
    mock_request.headers = {}
    
    ip = error_handler.get_client_ip(mock_request)
    assert ip == "192.168.1.1"


def test_get_client_ip_with_proxy(error_handler):
    """测试代理情况下的客户端IP获取"""
    # 模拟请求对象
    mock_request = AsyncMock()
    mock_request.client.host = "192.168.1.1"
    mock_request.headers = {
        "x-forwarded-for": "203.0.113.1, 198.51.100.2",
        "x-real-ip": "203.0.113.1"
    }
    
    ip = error_handler.get_client_ip(mock_request)
    assert ip == "203.0.113.1"


def test_create_error_response(error_handler):
    """测试错误响应创建"""
    error_type = "test_error"
    message = "Test error message"
    status_code = 400
    details = {"field": "value"}
    
    response = error_handler.create_error_response(
        error_type, message, status_code, details
    )
    
    assert response["error"]["type"] == error_type
    assert response["error"]["message"] == message
    assert response["error"]["status_code"] == status_code
    assert response["error"]["details"] == details


if __name__ == "__main__":
    pytest.main([__file__])