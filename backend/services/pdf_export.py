# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""
PDF 双输出服务（原创实现，跨平台最佳努力）。

转换优先级：
  1. LibreOffice headless（soffice --headless --convert-to pdf）
  2. docx2pdf（Windows + 已安装 MS Word 时可用）
  3. 均不可用时抛出带指引的错误信息

LibreOffice 位置发现顺序：环境变量 LIBREOFFICE_PATH → PATH 中的 soffice/libreoffice
→ Windows 常见安装目录。
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger("official_doc_ai")

_WINDOWS_LO_CANDIDATES = (
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
)


def find_libreoffice() -> str | None:
    """定位 LibreOffice 可执行文件，找不到返回 None。"""
    env_path = __import__("os").environ.get("LIBREOFFICE_PATH", "").strip()
    if env_path and Path(env_path).exists():
        return env_path
    for name in ("soffice", "libreoffice", "soffice.bin"):
        found = shutil.which(name)
        if found:
            return found
    for candidate in _WINDOWS_LO_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    return None


def has_converter() -> bool:
    """是否存在可用转换器（LibreOffice 或 docx2pdf）。"""
    if find_libreoffice():
        return True
    try:
        import docx2pdf  # noqa: F401

        return True
    except ImportError:
        return False


def convert_docx_to_pdf(docx_path: str | Path, out_dir: str | Path | None = None) -> Path:
    """
    将 .docx 转换为 PDF，返回生成的 PDF 路径。

    Raises:
        RuntimeError: 无可用转换器或转换失败（信息含安装指引）。
    """
    docx = Path(docx_path)
    if not docx.exists():
        raise RuntimeError(f"源文件不存在: {docx}")
    out = Path(out_dir).resolve() if out_dir else docx.parent.resolve()
    out.mkdir(parents=True, exist_ok=True)

    # 1) LibreOffice headless
    soffice = find_libreoffice()
    if soffice:
        try:
            result = subprocess.run(
                [
                    soffice,
                    "--headless",
                    "--norestore",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    str(out),
                    str(docx.resolve()),
                ],
                capture_output=True,
                text=True,
                timeout=180,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"LibreOffice 转换失败: {result.stderr.strip() or '未知错误'}"
                )
            pdf = out / (docx.stem + ".pdf")
            if pdf.exists():
                logger.info("PDF export via LibreOffice: %s", pdf)
                return pdf
            # LO 偶尔将输出写到 cwd，兜底查找
            cwd_pdf = Path.cwd() / (docx.stem + ".pdf")
            if cwd_pdf.exists():
                cwd_pdf.replace(out / cwd_pdf.name)
                return out / cwd_pdf.name
            raise RuntimeError("LibreOffice 未产出 PDF（请检查文档是否损坏）")
        except subprocess.TimeoutExpired:
            raise RuntimeError("LibreOffice 转换超时（180s），请检查文档复杂度")

    # 2) docx2pdf（需本机安装 MS Word）
    try:
        from docx2pdf import convert as _d2p

        pdf = out / (docx.stem + ".pdf")
        _d2p(str(docx.resolve()), str(pdf))
        if pdf.exists():
            logger.info("PDF export via docx2pdf: %s", pdf)
            return pdf
        raise RuntimeError("docx2pdf 未产出 PDF")
    except ImportError:
        pass

    raise RuntimeError(
        "未找到 PDF 转换器。请安装 LibreOffice（推荐，跨平台开源）"
        "或 docx2pdf（Windows + MS Word），或在环境变量 LIBREOFFICE_PATH 中指定 soffice 路径。"
    )