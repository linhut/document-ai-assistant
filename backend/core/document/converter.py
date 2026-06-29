# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
文档格式转换器：将 .doc / .wps 转换为 .docx

使用 Windows COM 接口调用本地 Word 或 WPS Office 进行转换。
优先使用 Word COM，失败则回退到 WPS COM。
"""
from __future__ import annotations

import os
import time
from pathlib import Path

from utils.logger import logger

# 支持转换的扩展名（小写）
_CONVERTIBLE_EXTENSIONS = {".doc", ".wps"}

# Word COM 常量
_WD_FORMAT_DOCX = 16  # wdFormatXMLDocument


def is_convertible(filename: str) -> bool:
    """判断文件是否需要格式转换（.doc 或 .wps）。"""
    return Path(filename).suffix.lower() in _CONVERTIBLE_EXTENSIONS


def convert_to_docx(file_path: Path, output_dir: Path) -> Path:
    """
    将 .doc 或 .wps 文件转换为 .docx。

    Args:
        file_path: 原始文件路径
        output_dir: 输出目录

    Returns:
        转换后的 .docx 文件路径

    Raises:
        FileNotFoundError: 源文件不存在
        RuntimeError: 未安装 Word 或 WPS Office
        Exception: 转换失败
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"源文件不存在: {file_path}")

    suffix = file_path.suffix.lower()
    if suffix not in _CONVERTIBLE_EXTENSIONS:
        raise ValueError(f"不支持的格式: {suffix}，仅支持 .doc / .wps")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{file_path.stem}.docx"

    # 已经存在同名 docx 则先删除，确保使用最新转换结果
    if output_path.exists():
        try:
            output_path.unlink()
            logger.info(f"删除旧的输出文件: {output_path}")
        except OSError as e:
            logger.warning(f"删除旧输出文件失败: {e}，将覆盖写入")

    import sys
    converted = False

    if sys.platform == 'win32':
        # Windows: 优先 Word COM → WPS COM → LibreOffice
        converted = _try_word_com(file_path, output_path)
        if not converted:
            converted = _try_wps_com(file_path, output_path)
        if not converted:
            converted = _try_libreoffice(file_path, output_path)
    else:
        # Linux / macOS: LibreOffice headless（信创系统通常预装）
        converted = _try_libreoffice(file_path, output_path)

    if not converted:
        raise RuntimeError(
            "文档转换失败：未检测到 Microsoft Word、WPS Office 或 LibreOffice。\n"
            "Windows: 请安装 Word 或 WPS。\n"
            "Linux: 请安装 LibreOffice（sudo apt install libreoffice-common）。"
        )

    logger.info(f"格式转换成功: {file_path.name} → {output_path.name}")
    return output_path


def _try_word_com(file_path: Path, output_path: Path) -> bool:
    """尝试使用 Word COM 转换。"""
    try:
        import win32com.client
        import pythoncom

        pythoncom.CoInitialize()
        word = None
        doc = None
        try:
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            word.DisplayAlerts = 0  # wdAlertsNone

            src = str(file_path.resolve())
            dst = str(output_path.resolve())

            doc = word.Documents.Open(src, ReadOnly=True)
            doc.SaveAs(dst, FileFormat=_WD_FORMAT_DOCX)
            doc.Close(SaveChanges=False)
            doc = None

            logger.info(f"Word COM 转换成功: {file_path.name}")
            return True
        except Exception as e:
            logger.debug(f"Word COM 转换失败: {e}")
            return False
        finally:
            if doc:
                try:
                    doc.Close(SaveChanges=False)
                except Exception:
                    pass
            if word:
                try:
                    word.Quit()
                except Exception:
                    pass
            pythoncom.CoUninitialize()
    except ImportError:
        logger.debug("pywin32 未安装，跳过 Word COM")
        return False


def _try_wps_com(file_path: Path, output_path: Path) -> bool:
    """尝试使用 WPS COM 转换（kwps.Application）。"""
    try:
        import win32com.client
        import pythoncom

        pythoncom.CoInitialize()
        wps = None
        doc = None

        # WPS COM 注册名可能是 kwps.Application 或 wps.Application
        for prog_id in ("kwps.Application", "wps.Application"):
            try:
                wps = win32com.client.Dispatch(prog_id)
                break
            except Exception:
                continue

        if wps is None:
            logger.debug("WPS COM 不可用")
            return False

        try:
            wps.Visible = False

            src = str(file_path.resolve())
            dst = str(output_path.resolve())

            doc = wps.Documents.Open(src)
            doc.SaveAs2(dst, FileFormat=_WD_FORMAT_DOCX)
            doc.Close()
            doc = None

            logger.info(f"WPS COM 转换成功: {file_path.name}")
            return True
        except Exception as e:
            logger.debug(f"WPS COM 转换失败: {e}")
            return False
        finally:
            if doc:
                try:
                    doc.Close()
                except Exception:
                    pass
            if wps:
                try:
                    wps.Quit()
                except Exception:
                    pass
            pythoncom.CoUninitialize()
    except ImportError:
        logger.debug("pywin32 未安装，跳过 WPS COM")
        return False


def _try_libreoffice(file_path: Path, output_path: Path) -> bool:
    """
    使用 LibreOffice headless 模式转换 .doc/.wps → .docx。

    Linux/macOS（含信创 UOS/Kylin）上的主要转换方式。
    信创系统通常预装 LibreOffice 或 WPS。
    """
    import subprocess
    import shutil

    # 查找 libreoffice 可执行文件
    lo_cmd = shutil.which('libreoffice') or shutil.which('soffice')
    if not lo_cmd:
        # 尝试常见安装路径
        for candidate in [
            '/usr/bin/libreoffice',
            '/usr/bin/soffice',
            '/opt/libreoffice/program/soffice',
            '/usr/local/bin/libreoffice',
        ]:
            if Path(candidate).exists():
                lo_cmd = candidate
                break

    if not lo_cmd:
        logger.debug("LibreOffice 未安装，跳过 headless 转换")
        return False

    try:
        src = str(file_path.resolve())
        dst_dir = str(output_path.parent.resolve())

        result = subprocess.run(
            [lo_cmd, '--headless', '--convert-to', 'docx', '--outdir', dst_dir, src],
            capture_output=True, text=True, timeout=120,
        )

        if result.returncode == 0 and output_path.exists():
            logger.info(f"LibreOffice headless 转换成功: {file_path.name}")
            return True
        else:
            logger.debug(f"LibreOffice 转换失败: {result.stderr[:200]}")
            return False
    except FileNotFoundError:
        logger.debug("LibreOffice 可执行文件不存在")
        return False
    except subprocess.TimeoutExpired:
        logger.warning("LibreOffice 转换超时（120s）")
        return False
    except Exception as e:
        logger.debug(f"LibreOffice 转换异常: {e}")
        return False
