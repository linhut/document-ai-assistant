# Linux/macOS 代码级兼容检查报告

> 检查日期：2026-09-12 | 方式：**代码级静态检查**（无法在 Linux/macOS 实机回归，按要求以代码审查代替）
> 范围：平台相关代码、路径与编码、子进程调用、字体处理、依赖清单

## 一、平台相关代码清单（逐处评估）

| 位置 | 平台相关点 | 平台分支 | 评估 |
|---|---|---|---|
| `core/document/converter.py` | .doc/.wps 转换 | `sys.platform == "win32"` → Word COM → WPS COM；非 Windows → LibreOffice headless | ✅ 跨平台；Linux 报错信息给出 `sudo apt install libreoffice-common` 指引 |
| `main.py` `_find_pid_on_port/_kill_pid` | 端口占用检测/清理 | `sys.platform != "win32"` 直接返回 None/False | ⚠️ 非 Windows 上 `--force` 不生效（端口占用时需手动处理），可接受 |
| `services/pdf_export.py` | PDF 转换 | `LIBREOFFICE_PATH` → `shutil.which(soffice/libreoffice)` → Windows 候选路径 | ✅ 跨平台发现逻辑；macOS 可 brew 安装 LibreOffice |
| `utils/crypto.py` | 密钥文件权限 | POSIX `os.chmod(0o600)`；Windows `icacls` | ✅ 双平台分支 |
| `frozen_main.py` | PyInstaller 工作目录 | `os.path.dirname(sys.executable)` + `os.chdir` | ✅ 纯 os.path，Linux/macOS 打包同名逻辑可用 |
| `requirements.txt` | pywin32 | `pywin32>=306; sys_platform == 'win32'` | ✅ 条件依赖，Linux/macOS 安装不拉取 pywin32 |

**子进程调用清单**（共 4 处，均跨平台安全）：
1. `converter.py`：`soffice --headless --convert-to docx`（跨平台命令）
2. `pdf_export.py`：`soffice --headless --convert-to pdf`（跨平台命令）
3. `main.py`：`netstat -ano` / `taskkill`（仅 win32 分支内执行）
4. `crypto.py`：`icacls`（仅 win32 分支内执行）

## 二、路径与编码

- 全部使用 `pathlib.Path`，无硬编码路径分隔符（未发现 `C:\`、`/Users/` 等平台特定绝对路径散落业务代码）
- 文件读写均显式 `encoding="utf-8"`（YAML/JSON/日志抽查通过）
- `config.py` 的 `APP_DATA_DIR`/`RULES_DIR` 基于 `BASE_DIR` 派生，打包与开发两模式共用同一套路径逻辑

## 三、字体处理

- 字体目录 `TTF/`：方正小标宋简、仿宋_GB2312、楷体_GB2312（跨平台随包分发）
- 生成器对缺字体做**警告/拒绝替代**（`--require-standard-fonts` 语义），不依赖系统字体名称假设
- Word/WPS 字体兼容性由 `font_utils.set_run_font()` 四属性（ascii/hAnsi/eastAsia/cs）保证，与平台无关
- ⚠️ 视觉回归的 PDF→PNG 渲染在 Linux CI 上的字体渲染与本地 Windows 可能有细微差异——已通过 `continue-on-error` + docx sha256 双轨基线缓解

## 四、依赖清单（跨平台性）

`fastapi / uvicorn / python-docx / pydantic / sqlalchemy / pyyaml / cryptography / httpx / python-multipart / aiofiles` 均为跨平台纯 Python 包；`pywin32` 已用环境标记限定 win32。前端构建（node）三平台脚本齐备（`electron:build:linux*`、mac dmg 目标已配置）。

## 五、结论与残余风险

**结论：代码级兼容性检查通过，未发现阻塞性平台问题。**

| 级别 | 风险 | 缓解/说明 |
|---|---|---|
| 低 | 非 Windows 上 `--force` 端口清理不生效 | 属增强能力缺失，非缺陷；文档说明即可 |
| 低 | Linux/macOS 无 docx2pdf 路径 | LibreOffice 为推荐方案，错误信息已指引 |
| 中 | 视觉渲染字体差异 | CI 双轨基线 + continue-on-error |
| 待实机 | PyInstaller 产物、electron-builder 各平台安装包、LibreOffice 实转、PyMuPDF 渲染 | 需在目标环境执行 `pytest tests/` + `npm run electron:build:linux*` 复验（如实说明，未在本机完成） |

## 六、本轮新增代码的专项结论

本轮新增（semantic / special_layout / content_diff / dark_bid / packs / style_library / pdf_export / vr_lib / 前端 store）经扫描：
- 零 `os.system`、零 `win32`/`WindowsError` 硬编码；
- 路径操作全部 pathlib；
- 双平台安装脚本（`skill/scripts/install.sh` + `install.ps1`）已随 SKILL 包提供。
