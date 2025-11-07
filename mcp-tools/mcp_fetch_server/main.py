#!/usr/bin/env python3
"""
MCP Fetch Server - Streamable HTTP Transport

A Model Context Protocol server that provides HTTP fetching capabilities
with Streamable HTTP transport support.
"""

import asyncio
import logging
import argparse
import signal
import sys
from typing import Optional

from .server import FetchMCPServer


def setup_logging(level: str = "INFO"):
    """设置日志配置"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


async def shutdown(server: FetchMCPServer, signal: Optional[signal.Signals] = None):
    """优雅关闭服务器"""
    if signal:
        logging.info(f"Received exit signal {signal.name}...")
    
    logging.info("Shutting down MCP fetch server...")
    await server.stop()
    
    # 取消所有正在运行的任务
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    
    await asyncio.gather(*tasks, return_exceptions=True)
    logging.info("Server shutdown complete")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="MCP Fetch Server with Streamable HTTP transport"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level (default: INFO)"
    )
    parser.add_argument(
        "--name",
        type=str,
        default="mcp-fetch-server",
        help="Server name (default: mcp-fetch-server)"
    )
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # 创建服务器实例
    server = FetchMCPServer(name=args.name)
    
    async def run_server():
        """运行服务器"""
        # 设置信号处理
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, lambda s, _: asyncio.create_task(shutdown(server, s)))
        
        try:
            logger.info(f"Starting {args.name} on {args.host}:{args.port}")
            await server.start(host=args.host, port=args.port)
        except Exception as e:
            logger.error(f"Server error: {e}")
            await shutdown(server)
            sys.exit(1)
    
    # 运行服务器
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt, shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()