# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
全局配置

路径分层：
  BASE_DIR     — 只读资源（rules/official, templates/official, TTF 字体）
  APP_DATA_DIR — 可写运行时数据（数据库、日志、上传、输出、用户规则/模板）

开发模式：两者相同，均指向项目根目录。
生产模式：BASE_DIR 指向安装目录 resources/，APP_DATA_DIR 指向 Electron userData。
"""
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
#  BASE_DIR: 只读资源根目录
# ---------------------------------------------------------------------------
if getattr(sys, 'frozen', False):
    # PyInstaller 打包后：exe 在 resources/backend_server/ 中，
    # BASE_DIR 指向上级 resources/ 目录（与 rules/、templates/、TTF/ 同级）
    BASE_DIR = Path(sys.executable).resolve().parent.parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
#  APP_DATA_DIR: 可写运行时数据目录
# ---------------------------------------------------------------------------
# 优先从环境变量获取（由 Electron main 进程在生产模式下传入）
_env_app_data = os.environ.get("APP_DATA_DIR")
if _env_app_data:
    APP_DATA_DIR = Path(_env_app_data)
else:
    # 开发模式或未设置时，使用项目根目录下的 data/
    APP_DATA_DIR = BASE_DIR / "data"

# ---------------------------------------------------------------------------
#  数据库
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{APP_DATA_DIR / 'app.db'}"
)

# ---------------------------------------------------------------------------
#  可写目录（运行时数据 → APP_DATA_DIR）
# ---------------------------------------------------------------------------
UPLOAD_DIR = APP_DATA_DIR / "uploads"
OUTPUT_DIR = APP_DATA_DIR / "outputs"
LOG_DIR = APP_DATA_DIR / "logs"
TEMP_DIR = APP_DATA_DIR / "tmp"
USER_RULES_DIR = APP_DATA_DIR / "user_rules"
CUSTOM_RULES_DIR = APP_DATA_DIR / "custom_rules"
USER_TEMPLATES_DIR = APP_DATA_DIR / "user_templates"

# ---------------------------------------------------------------------------
#  只读目录（捆绑资源 → BASE_DIR）
# ---------------------------------------------------------------------------
RULES_DIR = BASE_DIR / "rules" / "official"

# ---------------------------------------------------------------------------
#  其他配置
# ---------------------------------------------------------------------------
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")
API_PORT = int(os.getenv("API_PORT", "8765"))

# ---------------------------------------------------------------------------
#  自动创建所有必需目录
# ---------------------------------------------------------------------------
_writable_dirs = [
    UPLOAD_DIR, OUTPUT_DIR, LOG_DIR, TEMP_DIR,
    USER_RULES_DIR, CUSTOM_RULES_DIR, USER_TEMPLATES_DIR,
]
for _d in _writable_dirs:
    _d.mkdir(parents=True, exist_ok=True)
