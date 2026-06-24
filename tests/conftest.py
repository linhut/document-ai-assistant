"""
conftest.py — 为测试添加 backend 目录到 sys.path
"""
import sys
from pathlib import Path

# 将 backend/ 加入 Python path
_backend = Path(__file__).resolve().parent.parent / "backend"
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))