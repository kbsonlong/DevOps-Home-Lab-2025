import logging
import sys
from typing import Dict, Any


class ErrorHandler:
    """错误处理和日志管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
    
    def setup_logging(self, level: str = "INFO"):
        """设置日志配置"""
        # 创建日志格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        # 文件处理器
        file_handler = logging.FileHandler('mcp-fetch-server.log')
        file_handler.setFormatter(formatter)
        
        # 配置根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper()))
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        
        # 配置特定模块的日志级别
        logging.getLogger('uvicorn').setLevel(logging.WARNING)
        logging.getLogger('aiohttp').setLevel(logging.WARNING)
        
        self.logger = logging.getLogger(__name__)
    
    def log_request(self, method: str, url: str, status: int, duration: float):
        """记录HTTP请求日志"""
        self.logger.info(
            f"HTTP {method} {url} - Status: {status} - Duration: {duration:.3f}s"
        )
    
    def log_error(self, error_type: str, message: str, context: Dict[str, Any] = None):
        """记录错误日志"""
        error_msg = f"{error_type}: {message}"
        if context:
            error_msg += f" - Context: {context}"
        self.logger.error(error_msg)
    
    def log_warning(self, warning_type: str, message: str, context: Dict[str, Any] = None):
        """记录警告日志"""
        warning_msg = f"{warning_type}: {message}"
        if context:
            warning_msg += f" - Context: {context}"
        self.logger.warning(warning_msg)
    
    def log_info(self, info_type: str, message: str, context: Dict[str, Any] = None):
        """记录信息日志"""
        info_msg = f"{info_type}: {message}"
        if context:
            info_msg += f" - Context: {context}"
        self.logger.info(info_msg)
    
    def log_debug(self, debug_type: str, message: str, context: Dict[str, Any] = None):
        """记录调试日志"""
        debug_msg = f"{debug_type}: {message}"
        if context:
            debug_msg += f" - Context: {context}"
        self.logger.debug(debug_msg)
    
    def handle_exception(self, exception: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理异常并返回错误响应"""
        error_type = type(exception).__name__
        error_message = str(exception)
        
        # 记录异常
        self.log_error(error_type, error_message, context)
        
        # 根据异常类型返回适当的错误响应
        if isinstance(exception, ValueError):
            return {
                "error": {
                    "code": -32602,
                    "message": "Invalid params",
                    "data": error_message
                }
            }
        elif isinstance(exception, TimeoutError):
            return {
                "error": {
                    "code": -32000,
                    "message": "Request timeout",
                    "data": error_message
                }
            }
        elif isinstance(exception, ConnectionError):
            return {
                "error": {
                    "code": -32001,
                    "message": "Connection error",
                    "data": error_message
                }
            }
        else:
            return {
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": error_message
                }
            }
    
    def validate_url(self, url: str) -> bool:
        """验证URL格式"""
        from urllib.parse import urlparse
        
        try:
            result = urlparse(url)
            is_valid = all([result.scheme, result.netloc])
            
            if not is_valid:
                self.log_warning("URL_VALIDATION", f"Invalid URL format: {url}")
            
            return is_valid
        except Exception as e:
            self.log_error("URL_VALIDATION_ERROR", f"Error validating URL {url}: {e}")
            return False
    
    def sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """清理和验证HTTP头"""
        sanitized = {}
        
        for key, value in headers.items():
            # 移除潜在的危险头
            if key.lower() not in ['host', 'content-length', 'transfer-encoding']:
                sanitized[key] = value
            else:
                self.log_warning("HEADER_SANITIZATION", f"Removed potentially dangerous header: {key}")
        
        return sanitized
    
    def check_rate_limit(self, client_id: str, max_requests: int = 100, time_window: int = 60) -> bool:
        """简单的速率限制检查（可根据需要扩展）"""
        # 这里可以实现更复杂的速率限制逻辑
        # 现在只是一个占位符
        return True
    
    def get_client_ip(self, request) -> str:
        """获取客户端IP地址"""
        # 处理代理情况
        if hasattr(request, 'headers'):
            forwarded_for = request.headers.get('X-Forwarded-For')
            if forwarded_for:
                return forwarded_for.split(',')[0].strip()
            
            real_ip = request.headers.get('X-Real-IP')
            if real_ip:
                return real_ip
        
        # 默认返回客户端地址
        if hasattr(request, 'client') and request.client:
            return request.client.host
        
        return "unknown"