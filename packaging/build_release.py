#!/usr/bin/env python3
"""
(c) 2026 Jose AI (https://www.linhut.cn)
Licensed under the MIT License. See the LICENSE file for details.

多平台打包脚本

支持打包目标：
  1. PyInstaller 后端 (backend_server.exe)
  2. Electron 前端 (NSIS 安装包 / AppImage / DMG)
  3. 便携版 (zip)
  4. CLI 独立包

用法：
  python build_release.py --target all
  python build_release.py --target backend
  python build_release.py --target frontend --platform win-x64
  python build_release.py --target portable
  python build_release.py --target cli
"""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
PACKAGING_DIR = ROOT_DIR / "packaging"
OUTPUT_DIR = PACKAGING_DIR / "dist"

# 版本号
def get_version():
    pkg = json.loads((FRONTEND_DIR / "package.json").read_text(encoding="utf-8"))
    return pkg.get("version", "0.0.0")


def log(msg):
    print(f"[build] {msg}")


def run(cmd, cwd=None):
    log(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd or str(ROOT_DIR), capture_output=True, text=True)
    if result.returncode != 0:
        log(f"STDERR: {result.stderr[:500]}")
        raise RuntimeError(f"Command failed: {cmd}")
    return result.stdout


def build_backend():
    """PyInstaller 打包后端"""
    log("=== Building backend (PyInstaller) ===")

    pyinstaller_args = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "backend_server",
        "--add-data", f"{BACKEND_DIR / 'core'};core",
        "--add-data", f"{BACKEND_DIR / 'api'};api",
        "--add-data", f"{BACKEND_DIR / 'ai'};ai",
        "--add-data", f"{BACKEND_DIR / 'db'};db",
        "--add-data", f"{BACKEND_DIR / 'services'};services",
        "--add-data", f"{BACKEND_DIR / 'utils'};utils",
        "--add-data", f"{ROOT_DIR / 'rules'};rules",
        "--add-data", f"{ROOT_DIR / 'templates'};templates",
        "--hidden-import", "uvicorn",
        "--hidden-import", "fastapi",
        "--hidden-import", "sqlalchemy",
        "--hidden-import", "pydantic",
        "--hidden-import", "httpx",
        "--hidden-import", "docx",
        str(BACKEND_DIR / "main.py"),
    ]

    result = subprocess.run(pyinstaller_args, capture_output=True, text=True, cwd=str(ROOT_DIR))
    if result.returncode != 0:
        log(f"PyInstaller STDERR: {result.stderr[:1000]}")
        raise RuntimeError("PyInstaller build failed")

    log("Backend build complete")


def build_frontend(platform_target="win-x64"):
    """Electron 前端打包"""
    log(f"=== Building frontend ({platform_target}) ===")

    # 1. Vite build
    run("npm run build", cwd=str(FRONTEND_DIR))

    # 2. Electron build
    electron_cmd = "npm run electron:build:preview"
    if platform_target == "win-x64":
        electron_cmd = "npm run electron:build:win"
    elif platform_target == "win-arm64":
        electron_cmd = "npm run electron:build:win -- --arm64"
    elif platform_target == "linux-x64":
        electron_cmd = "npm run electron:build:linux"
    elif platform_target == "mac-x64":
        electron_cmd = "npm run electron:build:mac"
    elif platform_target == "mac-arm64":
        electron_cmd = "npm run electron:build:mac -- --arm64"

    run(electron_cmd, cwd=str(FRONTEND_DIR))
    log(f"Frontend build complete for {platform_target}")


def build_portable():
    """便携版打包（zip）"""
    log("=== Building portable package ===")

    version = get_version()
    portable_name = f"doc-optimizer-v{version}-portable"
    portable_dir = OUTPUT_DIR / portable_name
    portable_zip = OUTPUT_DIR / f"{portable_name}.zip"

    # 清理
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    portable_dir.mkdir(parents=True, exist_ok=True)

    # 复制后端
    backend_dist = ROOT_DIR / "dist" / "backend_server"
    if backend_dist.exists():
        shutil.copytree(backend_dist, portable_dir / "backend_server")

    # 复制前端
    frontend_dist = FRONTEND_DIR / "dist"
    if frontend_dist.exists():
        shutil.copytree(frontend_dist, portable_dir / "frontend")

    # 复制规则和模板
    for d in ["rules", "templates", "data"]:
        src = ROOT_DIR / d
        if src.exists():
            shutil.copytree(src, portable_dir / d)

    # 创建启动脚本
    start_bat = portable_dir / "start.bat"
    start_bat.write_text(
        '@echo off\ncd /d "%~dp0"\nstart backend_server\\backend_server.exe --port 8765\n'
        'timeout /t 3 >nul\nstart frontend\\index.html\n',
        encoding="utf-8",
    )

    # 打包为 zip
    with zipfile.ZipFile(portable_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in portable_dir.rglob("*"):
            if file.is_file():
                zf.write(file, file.relative_to(portable_dir))

    log(f"Portable package: {portable_zip}")
    shutil.rmtree(portable_dir)


def build_cli():
    """CLI 独立包"""
    log("=== Building CLI package ===")

    cli_args = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "doc-optimizer-cli",
        "--add-data", f"{BACKEND_DIR / 'core'};core",
        "--add-data", f"{BACKEND_DIR / 'utils'};utils",
        "--add-data", f"{ROOT_DIR / 'rules'};rules",
        "--hidden-import", "yaml",
        "--hidden-import", "docx",
        str(BACKEND_DIR / "wfp_cli.py"),
    ]

    result = subprocess.run(cli_args, capture_output=True, text=True, cwd=str(ROOT_DIR))
    if result.returncode != 0:
        log(f"CLI PyInstaller STDERR: {result.stderr[:1000]}")
        raise RuntimeError("CLI build failed")

    log("CLI build complete")


def create_changelog():
    """从 release notes 生成 CHANGELOG"""
    log("=== Creating CHANGELOG ===")

    release_notes = PACKAGING_DIR / f"release-notes-v{get_version()}.md"
    changelog = ROOT_DIR / "CHANGELOG.md"

    if release_notes.exists():
        content = release_notes.read_text(encoding="utf-8")
        if changelog.exists():
            existing = changelog.read_text(encoding="utf-8")
            changelog.write_text(content + "\n\n---\n\n" + existing, encoding="utf-8")
        else:
            changelog.write_text(content, encoding="utf-8")
        log(f"CHANGELOG updated: {changelog}")
    else:
        log(f"Release notes not found: {release_notes}")


def main():
    parser = argparse.ArgumentParser(description="多平台打包脚本")
    parser.add_argument("--target", choices=["all", "backend", "frontend", "portable", "cli", "changelog"],
                        default="all", help="打包目标")
    parser.add_argument("--platform", default="win-x64",
                        choices=["win-x64", "win-arm64", "linux-x64", "mac-x64", "mac-arm64"],
                        help="目标平台")
    args = parser.parse_args()

    version = get_version()
    log(f"Building version {version}")
    log(f"Platform: {args.platform}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.target in ("all", "backend"):
        try:
            build_backend()
        except Exception as e:
            log(f"Backend build failed: {e}")

    if args.target in ("all", "frontend"):
        try:
            build_frontend(args.platform)
        except Exception as e:
            log(f"Frontend build failed: {e}")

    if args.target in ("all", "portable"):
        try:
            build_portable()
        except Exception as e:
            log(f"Portable build failed: {e}")

    if args.target in ("all", "cli"):
        try:
            build_cli()
        except Exception as e:
            log(f"CLI build failed: {e}")

    if args.target in ("all", "changelog"):
        create_changelog()

    log("=== Build complete ===")


if __name__ == "__main__":
    main()
