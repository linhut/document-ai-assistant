# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Settings API routes: rule types, general config, font download.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
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
