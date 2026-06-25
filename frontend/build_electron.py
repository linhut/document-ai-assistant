"""
build_electron.py — Windows electron-builder 完整包装脚本
自动处理 win-unpacked.tmp → win-unpacked 的 EPERM rename 问题
并确保 app.asar 正确打包
"""
import subprocess, shutil, os, sys, json

FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))
RELEASE_DIR = os.path.join(FRONTEND_DIR, "release")
TMP_DIR = os.path.join(RELEASE_DIR, "win-unpacked.tmp")
FINAL_DIR = os.path.join(RELEASE_DIR, "win-unpacked")
EXE_NAME = "AI-Document-Assistant.exe"


def fix_rename():
    """如果 .tmp 目录存在，手动 rename 到最终目录"""
    if os.path.exists(TMP_DIR):
        if os.path.exists(FINAL_DIR):
            shutil.rmtree(FINAL_DIR)
        shutil.move(TMP_DIR, FINAL_DIR)
        print(f"[fix] {TMP_DIR} -> {FINAL_DIR}")
    # 重命名 electron.exe
    electron_exe = os.path.join(FINAL_DIR, "electron.exe")
    target_exe = os.path.join(FINAL_DIR, EXE_NAME)
    if os.path.exists(electron_exe) and not os.path.exists(target_exe):
        os.rename(electron_exe, target_exe)
        print(f"[fix] electron.exe -> {EXE_NAME}")


def build_app_asar():
    """手动构建 app.asar 并复制到 resources 目录"""
    app_dir = os.path.join(FRONTEND_DIR, "release", "_app")
    if os.path.exists(app_dir):
        shutil.rmtree(app_dir)

    # 创建 app 目录结构
    os.makedirs(app_dir)

    # package.json (精简版)
    import json
    with open(os.path.join(FRONTEND_DIR, "package.json"), "r", encoding="utf-8") as f:
        pkg = json.load(f)

    app_pkg = {
        "name": pkg["name"],
        "version": pkg["version"],
        "main": "electron/dist/main.js",
        "author": pkg.get("author", ""),
        "description": pkg.get("description", ""),
    }
    with open(os.path.join(app_dir, "package.json"), "w", encoding="utf-8") as f:
        json.dump(app_pkg, f, indent=2)

    # 复制 dist 和 electron/dist
    for src_name in ("dist", os.path.join("electron", "dist")):
        src = os.path.join(FRONTEND_DIR, src_name)
        dst = os.path.join(app_dir, src_name)
        if os.path.exists(src):
            shutil.copytree(src, dst)
            print(f"[asar] copied {src_name}")

    # 用 asar 打包
    resources_dir = os.path.join(FINAL_DIR, "resources")
    asar_path = os.path.join(resources_dir, "app.asar")
    default_asar = os.path.join(resources_dir, "default_app.asar")
    if os.path.exists(default_asar):
        os.remove(default_asar)

    subprocess.run(
        f"npx asar pack \"{app_dir}\" \"{asar_path}\"",
        cwd=FRONTEND_DIR, shell=True, check=True
    )
    print(f"[asar] packed -> {asar_path}")

    # 清理临时 app 目录
    shutil.rmtree(app_dir)


def main():
    # Step 1: 清理旧的 release 目录
    if os.path.exists(RELEASE_DIR):
        shutil.rmtree(RELEASE_DIR)
        print("[clean] removed release/")

    # Step 2: 运行 electron-builder
    print("[build] running electron-builder...")
    sys.stdout.flush()

    # 先清理可能残留的 .tmp 目录
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR, ignore_errors=True)

    proc = subprocess.Popen(
        "npx electron-builder --win --x64 --publish=never",
        cwd=FRONTEND_DIR,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output_bytes = b""
    while True:
        chunk = proc.stdout.read(1)
        if not chunk:
            break
        output_bytes += chunk
    proc.wait()
    output = output_bytes.decode("utf-8", errors="replace")

    if proc.returncode != 0:
        if "EPERM" in output or os.path.exists(TMP_DIR):
            print("[build] EPERM detected, applying fix...")
            fix_rename()
            build_app_asar()

            print("[build] creating installer from prepackaged dir...")
            sys.stdout.flush()
            result2 = subprocess.run(
                f"npx electron-builder --win --x64 --publish=never --prepackaged \"{FINAL_DIR}\"",
                cwd=FRONTEND_DIR, shell=True,
            )
            sys.exit(result2.returncode)
        else:
            print(f"[build] failed:\n{output[-1000:]}")
            sys.exit(1)
    else:
        print("[build] success!")
        sys.exit(0)


if __name__ == "__main__":
    main()
