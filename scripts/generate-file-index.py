"""
生成 website/tmp/files.json 和 website/tmp/files.js — 扫描 TMP 目录并输出文件清单。
  files.js 通过 <script> 标签注入数据，兼容 file:// 协议（本地直接打开 HTML）。
  files.json 供 HTTP 部署（Nginx / GitHub Pages）使用。

运行： python scripts/generate-file-index.py
适用于纯静态部署（无需后端 API）。
"""
import json, os, time
from pathlib import Path

# 项目根目录
ROOT = Path(__file__).resolve().parent.parent
WEBSITE_TMP = ROOT / "website" / "tmp"
OUTPUT_JSON = WEBSITE_TMP / "files.json"
OUTPUT_JS   = WEBSITE_TMP / "files.js"

if not WEBSITE_TMP.exists():
    print(f"[WARN] 目录不存在: {WEBSITE_TMP}")
    os._exit(0)

files = []
for entry in sorted(WEBSITE_TMP.iterdir(), key=lambda e: e.stat().st_mtime, reverse=True):
    if not entry.is_file() or entry.name in ("files.json", "files.js"):
        continue
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

    sz = stat.st_size
    if sz < 1024:
        size_disp = f"{sz} B"
    elif sz < 1048576:
        size_disp = f"{sz / 1024:.1f} KB"
    else:
        size_disp = f"{sz / 1048576:.1f} MB"

    files.append({
        "name": entry.name,
        "size": sz,
        "size_display": size_disp,
        "mtime": stat.st_mtime,
        "mtime_display": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
        "type": file_type,
    })

data = {"files": files, "count": len(files), "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S")}

OUTPUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
OUTPUT_JS.write_text(
    "window.__FILE_DATA = " + json.dumps(data, ensure_ascii=False) + ";",
    encoding="utf-8",
)
print(f"✓ {OUTPUT_JSON} ({os.path.getsize(OUTPUT_JSON)} bytes)")
print(f"✓ {OUTPUT_JS}   ({os.path.getsize(OUTPUT_JS)} bytes)")
print(f"  → {len(files)} 个文件")
