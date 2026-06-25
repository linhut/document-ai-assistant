# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
PyInstaller 打包入口

当以 frozen 模式运行时（PyInstaller 打包的 exe），
此脚本设置正确的工作目录后启动 FastAPI 应用。

支持 --force 参数：端口被占用时自动杀死旧进程。
"""
import sys
import os

if getattr(sys, 'frozen', False):
    # PyInstaller 打包模式
    # exe 位于 resources/backend_server/backend_server.exe
    # 工作目录设为 resources/（即 BASE_DIR）
    exe_dir = os.path.dirname(sys.executable)
    base_dir = os.path.dirname(exe_dir)
    os.chdir(base_dir)

import argparse
import uvicorn
from main import app, _check_and_free_port, _setup_signal_handlers, HOST, DEFAULT_PORT

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI 公文智能优化助手后端")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="监听端口")
    parser.add_argument("--force", action="store_true", help="端口被占用时自动杀死旧进程")
    args = parser.parse_args()

    _setup_signal_handlers()
    _check_and_free_port(args.port, force=args.force)
    uvicorn.run(app, host=HOST, port=args.port)
