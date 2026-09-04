# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""
工作台 API — 列出 website/tmp 目录中的文件，供前端展示和打开。
同时同步写入 website/tmp/files.json，使纯静态部署也能获取最新清单。
"""

import json
import time
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from config import BASE_DIR

router = APIRouter(tags=["workspace"])

# 网站 tmp 目录（相对于项目根目录的 website/tmp）
WEBSITE_TMP_DIR = BASE_DIR / "website" / "tmp"
# 静态索引文件（前端 JS 直接读取）
STATIC_JSON = WEBSITE_TMP_DIR / "files.json"
STATIC_JS = WEBSITE_TMP_DIR / "files.js"


@router.get("/api/workspace/files")
async def list_workspace_files():
    """列出 website/tmp 目录下的所有文件，返回文件名、大小、修改时间和类型。

    每次调用同时更新 website/tmp/files.json，确保静态源始终保持最新。
    """
    tmp_dir = WEBSITE_TMP_DIR

    if not tmp_dir.exists():
        return JSONResponse(
            status_code=200,
            content={"files": [], "message": "tmp 目录不存在"},
        )

    try:
        files = []
        for entry in sorted(tmp_dir.iterdir(), key=lambda e: e.stat().st_mtime, reverse=True):
            if entry.is_file() and entry.name != "files.json":
                stat = entry.stat()
                ext = entry.suffix.lower()

                if ext in (".pdf",):
                    file_type = "pdf"
                elif ext in (".html", ".htm"):
                    file_type = "html"
                elif ext in (".docx", ".doc"):
                    file_type = "docx"
                elif ext in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"):
                    file_type = "image"
                elif ext in (".txt",):
                    file_type = "text"
                else:
                    file_type = "other"

                files.append(
                    {
                        "name": entry.name,
                        "size": stat.st_size,
                        "size_display": _format_size(stat.st_size),
                        "mtime": stat.st_mtime,
                        "mtime_display": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                        "type": file_type,
                    }
                )

        payload = {"files": files, "count": len(files), "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S")}

        # 同步写入静态 JSON 索引，便于纯静态部署
        _write_static_index(payload)

        return JSONResponse(status_code=200, content=payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取 tmp 目录失败: {str(e)}")


def _write_static_index(payload: dict) -> None:
    """将文件清单写入 website/tmp/files.json 和 files.js（供无需后端的静态部署使用）。"""
    try:
        STATIC_JSON.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        # JS 版本 — 通过 <script> 标签注入全局变量，兼容 file:// 协议
        STATIC_JS.write_text(
            "window.__FILE_DATA = " + json.dumps(payload, ensure_ascii=False) + ";",
            encoding="utf-8",
        )
    except Exception as e:
        print(f"[workspace] WARNING: 写入静态索引失败: {e}")


def _format_size(size: int) -> str:
    """将字节数转为可读格式。"""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.1f} GB"
