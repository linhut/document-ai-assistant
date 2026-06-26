# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Settings API routes: rule types, general config, font download.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path

from api.schemas.api_models import RuleTypeResponse
from core.rules.engine import RuleEngine
from config import BASE_DIR
from utils.logger import logger

router = APIRouter()

# 字体目录
FONTS_DIR = BASE_DIR / "TTF"


@router.get("/rule-types", response_model=RuleTypeResponse)
async def get_rule_types():
    """List available document types with rule files."""
    types = RuleEngine.available_types()
    return RuleTypeResponse(types=types)


@router.get("/health")
async def settings_health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
#  字体下载
# ---------------------------------------------------------------------------

@router.get("/fonts")
async def list_fonts():
    """列出可用的公文字体文件。"""
    fonts = []
    if FONTS_DIR.exists():
        for f in sorted(FONTS_DIR.iterdir()):
            if f.suffix.lower() in ('.ttf', '.otf', '.ttc'):
                size_kb = f.stat().st_size / 1024
                fonts.append({
                    "filename": f.name,
                    "display_name": _get_display_name(f.name),
                    "size_kb": round(size_kb, 1),
                    "description": _get_font_description(f.name),
                })
    return {"fonts": fonts, "total": len(fonts)}


@router.get("/fonts/download/{filename}")
async def download_font(filename: str):
    """下载单个字体文件。"""
    # 安全检查：防止路径遍历
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    font_path = FONTS_DIR / filename
    if not font_path.exists():
        raise HTTPException(status_code=404, detail=f"Font not found: {filename}")

    return FileResponse(
        path=str(font_path),
        filename=filename,
        media_type="application/octet-stream",
    )


def _get_display_name(filename: str) -> str:
    """从文件名推断显示名称。"""
    name_map = {
        "仿宋_GB2312.ttf": "仿宋_GB2312",
        "方正小标宋简.TTF": "方正小标宋简体",
        "楷体_GB2312.TTF": "楷体_GB2312",
    }
    return name_map.get(filename, filename.rsplit('.', 1)[0])


def _get_font_description(filename: str) -> str:
    """获取字体用途说明。"""
    desc_map = {
        "仿宋_GB2312.ttf": "公文正文字体（GB/T 9704 标准）",
        "方正小标宋简.TTF": "公文标题字体（GB/T 9704 标准）",
        "楷体_GB2312.TTF": "公文小标题/引用字体",
    }
    return desc_map.get(filename, "公文字体")


# ---------------------------------------------------------------------------
#  网络访问设置（局域网共享）
# ---------------------------------------------------------------------------

import json
import socket

_NETWORK_CONFIG_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "network_config.json"


def _load_network_config() -> dict:
    """加载网络配置。"""
    if _NETWORK_CONFIG_FILE.exists():
        try:
            return json.loads(_NETWORK_CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"web_access_enabled": True, "port": 8765}


def _save_network_config(config: dict) -> None:
    """保存网络配置。"""
    _NETWORK_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    _NETWORK_CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


def _get_lan_ip() -> str:
    """获取本机局域网 IP（优先 192.168/10/172.16-31 段）。"""
    candidates = []
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if ip.startswith("127."):
                continue
            candidates.append(ip)
    except Exception:
        pass

    # 优先返回局域网地址
    for ip in candidates:
        if ip.startswith("192.168.") or ip.startswith("10."):
            return ip
    for ip in candidates:
        parts = ip.split(".")
        if len(parts) == 4 and parts[0] == "172" and 16 <= int(parts[1]) <= 31:
            return ip

    # 回退：通过 UDP 连接获取
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


@router.get("/network")
async def get_network_status():
    """获取当前网络访问状态。"""
    config = _load_network_config()
    lan_ip = _get_lan_ip()
    port = config.get("port", 8765)
    enabled = config.get("web_access_enabled", False)

    return {
        "web_access_enabled": enabled,
        "host": "0.0.0.0" if enabled else "127.0.0.1",
        "port": port,
        "lan_ip": lan_ip,
        "lan_url": f"http://{lan_ip}:{port}" if enabled else None,
        "localhost_url": f"http://127.0.0.1:{port}",
        "message": f"局域网用户可通过 {lan_ip}:{port} 访问" if enabled else "当前仅本机可访问",
    }


class NetworkToggleRequest(BaseModel):
    enabled: bool


@router.post("/network")
async def toggle_network_access(body: NetworkToggleRequest):
    """开启/关闭局域网网页访问。需要重启后端生效。"""
    config = _load_network_config()
    config["web_access_enabled"] = body.enabled
    _save_network_config(config)

    lan_ip = _get_lan_ip()
    port = config.get("port", 8765)

    return {
        "success": True,
        "web_access_enabled": body.enabled,
        "lan_ip": lan_ip,
        "port": port,
        "lan_url": f"http://{lan_ip}:{port}" if body.enabled else None,
        "need_restart": True,
        "message": f"已{'开启' if body.enabled else '关闭'}局域网访问，重启后端后生效",
    }
