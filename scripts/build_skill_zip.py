# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""
构建 gongwen-optimizer skill 的 zip 发行包（原创实现，跨平台）。

将 skill/ 目录（SKILL.md + scripts/）打包为 dist/gongwen-skill.zip，
供 TraeWork 等支持 zip 导入的平台使用。

用法：
  python scripts/build_skill_zip.py [--out dist/gongwen-skill.zip]
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skill"
OUT_DEFAULT = ROOT / "dist" / "gongwen-skill.zip"

# 打包白名单（按需扩展；.gitignore 类与缓存文件不入包）
INCLUDE_SUFFIXES = {".md", ".sh", ".ps1", ".py", ".yaml", ".yml"}
EXCLUDE_PARTS = {"__pycache__", ".git"}


def build_zip(out_path: Path = OUT_DEFAULT) -> Path:
    if not SKILL_DIR.exists():
        raise FileNotFoundError(f"skill 目录不存在: {SKILL_DIR}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(SKILL_DIR.rglob("*")):
            if file.is_dir() or any(part in EXCLUDE_PARTS for part in file.parts):
                continue
            if file.suffix.lower() not in INCLUDE_SUFFIXES:
                continue
            zf.write(file, file.relative_to(SKILL_DIR))
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="构建 gongwen-skill zip 发行包")
    parser.add_argument("--out", type=str, default=str(OUT_DEFAULT), help="输出 zip 路径")
    args = parser.parse_args()
    out = build_zip(Path(args.out))
    print(f"[skill-zip] 已生成: {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()