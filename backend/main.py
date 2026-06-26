"""
AI 公文智能优化助手 - FastAPI 后端入口

启动参数:
  --port PORT    监听端口 (默认 8765)
  --force        端口被占用时自动杀死旧进程
"""
import argparse
import atexit
import os
import signal
import socket
import subprocess
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import documents, check, optimize, ai, settings, templates, rules, template_download, office
from db.database import init_db
from utils.logger import logger

HOST = "127.0.0.1"
DEFAULT_PORT = 8765


# ---------------------------------------------------------------------------
# 端口占用检测 & 旧进程清理
# ---------------------------------------------------------------------------

def _find_pid_on_port(port: int) -> int | None:
    """查找占用指定端口的进程 PID (仅 Windows)。"""
    if sys.platform != "win32":
        return None
    try:
        output = subprocess.check_output(
            ["netstat", "-ano"], text=True, stderr=subprocess.DEVNULL,
        )
        for line in output.splitlines():
            if f":{port}" in line and "LISTENING" in line:
                parts = line.split()
                pid = int(parts[-1])
                if pid > 0:
                    return pid
    except Exception:
        pass
    return None


def _kill_pid(pid: int) -> bool:
    """强制终止指定 PID 及其子进程树 (仅 Windows)。"""
    if sys.platform != "win32":
        return False
    try:
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def _check_and_free_port(port: int, force: bool) -> None:
    """
    检测端口是否被占用；--force 时自动释放，否则报错退出。
    同时注册 atexit 钩子确保当前进程退出时清理端口。
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex((HOST, port)) != 0:
            return  # 端口空闲

    pid = _find_pid_on_port(port)

    if not force:
        msg = f"端口 {port} 已被占用"
        if pid:
            msg += f"（PID {pid}）"
        msg += "。请先关闭旧进程，或使用 --force 自动释放。"
        print(f"[startup] ERROR: {msg}", file=sys.stderr)
        sys.exit(1)

    if pid:
        print(f"[startup] --force: 终止占用端口 {port} 的进程 PID {pid} ...")
        if _kill_pid(pid):
            # 等待端口释放（最多 3 秒）
            import time
            for _ in range(30):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    if s.connect_ex((HOST, port)) != 0:
                        break
                time.sleep(0.1)
            print(f"[startup] 端口 {port} 已释放。")
        else:
            print(f"[startup] WARNING: 无法终止 PID {pid}，尝试直接启动...", file=sys.stderr)
    else:
        print(f"[startup] --force: 端口 {port} 被占用但无法确定 PID，尝试直接启动...", file=sys.stderr)


def _setup_signal_handlers() -> None:
    """注册信号处理，确保 Ctrl+C 时优雅退出。"""
    def _shutdown(signum, frame):
        print("\n[sutdown] 收到终止信号，正在关闭...")
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Official Document AI Assistant",
    description="AI 公文智能优化助手核心引擎 API",
    version="1.4.3",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8765",
        "http://127.0.0.1:8765",
        "file://",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(check.router, prefix="/api/check", tags=["check"])
app.include_router(optimize.router, prefix="/api/optimize", tags=["optimize"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
app.include_router(rules.router, prefix="/api/rules", tags=["rules"])
app.include_router(template_download.router, prefix="/api/template", tags=["template_download"])
app.include_router(office.router, prefix="/api/office", tags=["office"])


@app.on_event("startup")
async def startup():
    init_db()
    _init_default_ai_config()
    _log_directory_status()


def _log_directory_status():
    """启动时打印关键目录状态，便于排查打包问题。"""
    from config import RULES_DIR, UPLOAD_DIR, BASE_DIR
    from pathlib import Path

    dirs_to_check = {
        "BASE_DIR": BASE_DIR,
        "RULES_DIR": RULES_DIR,
        "UPLOAD_DIR": UPLOAD_DIR,
    }
    for name, d in dirs_to_check.items():
        exists = d.exists()
        count = len(list(d.glob("*"))) if exists else 0
        print(f"[startup] {name}: {d} (exists={exists}, items={count})")

    # 检查规则文件
    yaml_count = len(list(RULES_DIR.glob("*.yaml"))) if RULES_DIR.exists() else 0
    print(f"[startup] Rule YAML files: {yaml_count}")
    if yaml_count == 0:
        print(f"[startup] WARNING: No rule YAML files found at {RULES_DIR}!")
        print(f"[startup] Templates will show 'has_rules: false' and document check will return no issues.")


def _init_default_ai_config():
    """启动时自动初始化默认 AI 配置（如果数据库中没有或配置不完整）。"""
    import os
    default_api_key = os.environ.get("DEFAULT_AI_API_KEY", "")
    default_base_url = os.environ.get("DEFAULT_AI_BASE_URL", "https://cpa.linhut.cn/v1")
    default_model = os.environ.get("DEFAULT_AI_MODEL", "gpt-4o-mini")

    # 如果没有配置环境变量，跳过默认配置创建
    if not default_api_key:
        logger.info("No DEFAULT_AI_API_KEY env var set, skipping default AI config creation")
        return

    try:
        from db.database import SessionLocal
        from db.models import AIConfig
        from utils.crypto import encrypt_value

        db = SessionLocal()
        try:
            # 精确查询 custom（内置默认）provider
            existing = db.query(AIConfig).filter(AIConfig.provider == "custom").first()
            if not existing:
                # 无配置 → 创建默认
                default_config = AIConfig(
                    provider="custom",
                    api_key_encrypted=encrypt_value(default_api_key),
                    base_url=default_base_url,
                    model=default_model,
                    is_active=True,
                )
                db.add(default_config)
                db.commit()
                logger.info(f"Default AI config created: custom @ {default_base_url}")
            else:
                # 有配置但字段不完整 → 补全
                changed = False
                if not existing.base_url:
                    existing.base_url = default_base_url
                    changed = True
                if not existing.model:
                    existing.model = default_model
                    changed = True
                if changed:
                    db.commit()
                    logger.info("Fixed incomplete AI config")
                else:
                    print(f"[startup] AI config: {existing.provider} @ {existing.base_url} (active={existing.is_active})")
        finally:
            db.close()
    except Exception as e:
        print(f"[startup] AI config init error: {e}")


@app.get("/")
async def root():
    return {
        "app": "Official Document AI Assistant",
        "version": "1.4.3",
        "docs": "/docs",
        "health": "/api/health"
    }


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "1.4.0"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI 公文智能优化助手后端")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="监听端口")
    parser.add_argument("--force", action="store_true", help="端口被占用时自动杀死旧进程")
    parser.add_argument("--host", type=str, default=None, help="绑定地址（覆盖配置文件）")
    args = parser.parse_args()

    # 确定绑定地址：命令行参数 > 配置文件 > 默认值
    bind_host = args.host
    if not bind_host:
        try:
            cfg_path = Path(__file__).resolve().parent.parent / "data" / "network_config.json"
            if cfg_path.exists():
                import json as _json
                cfg = _json.loads(cfg_path.read_text(encoding="utf-8"))
                bind_host = "0.0.0.0" if cfg.get("web_access_enabled", True) else HOST
            else:
                bind_host = "0.0.0.0"  # 默认开启网页访问
        except Exception:
            bind_host = HOST

    _setup_signal_handlers()
    _check_and_free_port(args.port, force=args.force)

    if bind_host == "0.0.0.0":
        logger.info(f"Web access enabled: binding to 0.0.0.0:{args.port}")
    uvicorn.run(app, host=bind_host, port=args.port)
