# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
后端一键构建脚本

将 Python 后端通过 PyInstaller 打包为独立 exe，
并复制静态资源到 frontend/dist-resources/backend/ 供 electron-builder 使用。

用法：python build_backend.py
"""
import subprocess
import shutil
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"
SPEC_FILE = BACKEND_DIR / "backend_server.spec"
DIST_DIR = PROJECT_ROOT / "dist" / "backend_server"
RESOURCES_DIR = PROJECT_ROOT / "frontend" / "dist-resources" / "backend"


def run(cmd: list[str], cwd: str | Path | None = None):
    """执行命令，失败时退出。"""
    print(f">>> {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=False)
    if result.returncode != 0:
        print(f"ERROR: 命令失败 (exit {result.returncode})")
        sys.exit(result.returncode)


def install_deps():
    """安装 Python 依赖 + PyInstaller。"""
    print("\n[1/3] 安装依赖...")
    req_file = BACKEND_DIR / "requirements.txt"
    run([sys.executable, "-m", "pip", "install", "-r", str(req_file), "pyinstaller", "--quiet"])


def build_exe():
    """运行 PyInstaller 构建。"""
    print("\n[2/3] PyInstaller 构建中...")
    # 清理旧的构建产物
    for d in [BACKEND_DIR / "build", BACKEND_DIR / "dist"]:
        if d.exists():
            shutil.rmtree(d)
    run([
        sys.executable, "-m", "PyInstaller",
        str(SPEC_FILE),
        "--clean",
        "--noconfirm",
        "--distpath", str(PROJECT_ROOT / "dist"),
        "--workpath", str(BACKEND_DIR / "build"),
    ], cwd=BACKEND_DIR)

    exe_suffix = '.exe' if sys.platform == 'win32' else ''
    exe_path = DIST_DIR / f"backend_server{exe_suffix}"
    if not exe_path.exists():
        print(f"ERROR: 二进制文件未生成: {exe_path}")
        sys.exit(1)
    print(f"   二进制已生成: {exe_path}")


def sync_installer_version():
    """从 package.json 读取版本号，同步到 installer.nsh（仅 Windows NSIS）。"""
    if sys.platform != 'win32':
        return  # NSIS 安装脚本仅 Windows 需要
    import json, re
    pkg_file = PROJECT_ROOT / "frontend" / "package.json"
    nsh_file = PROJECT_ROOT / "frontend" / "build" / "installer.nsh"
    if not pkg_file.exists() or not nsh_file.exists():
        return
    with open(pkg_file, "r", encoding="utf-8") as f:
        version = json.load(f).get("version", "1.0.0")
    content = nsh_file.read_text(encoding="utf-8")
    new_content = re.sub(r"Version \d+\.\d+\.\d+", f"Version {version}", content)
    if new_content != content:
        nsh_file.write_text(new_content, encoding="utf-8")
        print(f"   installer.nsh 版本已同步为 {version}")
    else:
        print(f"   installer.nsh 版本已是 {version}，无需更新")


def copy_resources():
    """复制静态资源到 electron-builder 可用的目录。"""
    print("\n[3/3] 复制静态资源...")

    # 同步 installer.nsh 中的版本号（从 package.json 读取）
    sync_installer_version()

    # 清理旧的资源目录
    if RESOURCES_DIR.exists():
        shutil.rmtree(RESOURCES_DIR)
    RESOURCES_DIR.mkdir(parents=True, exist_ok=True)

    # 复制 PyInstaller 输出（backend_server/ 目录整体）
    dst_exe = RESOURCES_DIR / "backend_server"
    print(f"   复制 {DIST_DIR} -> {dst_exe}")
    shutil.copytree(DIST_DIR, dst_exe)

    # 复制静态资源（与 exe 同级，在 resources/ 下）
    static_resources = [
        ("rules", PROJECT_ROOT / "rules"),
        ("templates", PROJECT_ROOT / "templates"),
        ("TTF", PROJECT_ROOT / "TTF"),
    ]
    for name, src in static_resources:
        if src.exists():
            dst = RESOURCES_DIR / name
            print(f"   复制 {src} -> {dst}")
            shutil.copytree(src, dst)
        else:
            print(f"   警告: {src} 不存在，跳过")

    # 复制 data 目录中的初始文件（仅复制需要预置的文件，用户数据目录由运行时创建）
    data_src = PROJECT_ROOT / "data"
    data_dst = RESOURCES_DIR / "data"
    data_dst.mkdir(parents=True, exist_ok=True)

    # 加密密钥（关键：必须保留，否则已有 API key 配置将失效）
    key_file = data_src / ".encryption_key"
    if key_file.exists():
        shutil.copy2(key_file, data_dst / ".encryption_key")
        print(f"   复制加密密钥: {key_file}")

    # 预生成的模板文件
    templates_src = data_src / "templates"
    if templates_src.exists():
        templates_dst = data_dst / "templates"
        shutil.copytree(templates_src, templates_dst, dirs_exist_ok=True)
        print(f"   复制模板文件: {templates_src}")

    # 预置官方 .dotx 模板
    official_tpl_src = data_src / "official_templates"
    if official_tpl_src.exists():
        official_tpl_dst = data_dst / "official_templates"
        shutil.copytree(official_tpl_src, official_tpl_dst, dirs_exist_ok=True)
        print(f"   复制官方模板: {official_tpl_src}")

    print("\n构建完成！输出目录:")
    print(f"   PyInstaller 输出: {DIST_DIR}")
    print(f"   Electron 资源目录: {RESOURCES_DIR}")


if __name__ == "__main__":
    print("=" * 60)
    print("  公文格式优化器 — 后端构建")
    print("=" * 60)
    install_deps()
    build_exe()
    copy_resources()
    print("\n" + "=" * 60)
    print("  后端构建成功！可以运行 npm run electron:build:preview 打包安装程序。")
    print("=" * 60)
