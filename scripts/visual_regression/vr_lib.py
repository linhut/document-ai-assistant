# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""
视觉回归公共库（原创实现）。

- image_average_hash / hash_distance：基于 PIL 的平均感知哈希与汉明距离
- pdf_to_images：基于 PyMuPDF 将 PDF 页面渲染为 PNG
- doc_to_pngs：.docx → PDF（复用 services.pdf_export 的最佳努力转换）→ PNG
- golden_model / generate_golden：按文种生成黄金样本 docx

转换器不可用（无 LibreOffice/docx2pdf）时，PDF/PNG 相关链路自动跳过，
仅保留黄金样本生成与哈希纯函数逻辑，保证 CI 与本地均可运行。
"""

from __future__ import annotations

import hashlib
import logging
import os
import sys
from pathlib import Path

# 使 backend 可导入（脚本直接运行时）
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.document.generator import generate_docx  # noqa: E402
from core.document.models import DocumentModel, DocumentMetadata, Paragraph  # noqa: E402

logger = logging.getLogger("official_doc_ai")

GOLDEN_TYPES = ["notice", "report", "request", "meeting", "letter"]


def image_average_hash(image, size: int = 8) -> int:
    """
    平均感知哈希（aHash）：缩放为 size×size 灰度图，按像素均值生成 size*size 位哈希。
    两张视觉相似图的哈希汉明距离小。
    """
    from PIL import Image

    if isinstance(image, str) or isinstance(image, Path):
        image = Image.open(image)
    gray = image.convert("L").resize((size, size), Image.LANCZOS)
    pixels = list(gray.getdata())
    mean = sum(pixels) / len(pixels)
    digest = 0
    for i, p in enumerate(pixels):
        if p >= mean:
            digest |= 1 << i
    return digest


def hash_distance(a: int, b: int) -> int:
    """两个感知哈希的汉明距离（位不同的个数）。"""
    return bin(a ^ b).count("1")


def pdf_to_images(pdf_path: str | Path, dpi: int = 80) -> list:
    """
    使用 PyMuPDF 将 PDF 每页渲染为 PIL 图像（无 PyMuPDF 时返回空列表）。
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.warning("PyMuPDF (fitz) 未安装，跳过 PDF 渲染")
        return []
    images = []
    with fitz.open(str(pdf_path)) as doc:
        for page in doc:
            pix = page.get_pixmap(dpi=dpi)
            images.append(pix.tobytes("png"))
    return images


def doc_to_pngs(docx_path: str | Path, out_dir: str | Path) -> list[Path]:
    """docx → PDF → PNG 列表。任一环节不可用时返回空列表。"""
    from services.pdf_export import convert_docx_to_pdf

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    try:
        pdf = convert_docx_to_pdf(docx_path, out)
    except RuntimeError:
        logger.warning("PDF 转换不可用，视觉回归跳过渲染环节")
        return []
    images = pdf_to_images(pdf)
    if not images:
        return []
    pngs: list[Path] = []
    for i, png_bytes in enumerate(images, start=1):
        p = out / f"{Path(pdf).stem}_p{i}.png"
        p.write_bytes(png_bytes)
        pngs.append(p)
    return pngs


def file_sha256(path: str | Path) -> str:
    """文件 SHA-256（用于 docx 内容基线）。"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def golden_model(doc_type: str) -> DocumentModel:
    """构造五类文种的黄金样本模型（标题/正文/署名/日期，带角色标记）。"""
    titles = {
        "notice": "关于印发《示例方案》的通知",
        "report": "关于2026年上半年工作情况的报告",
        "request": "关于新建办公场所的请示",
        "meeting": "关于召开安全生产工作会议的纪要",
        "letter": "关于商请协助开展调研的函",
    }
    meta = DocumentMetadata(title=titles.get(doc_type, "示例公文"))
    texts = [
        (titles.get(doc_type, "示例公文"), "title"),
        ("各县（市、区）人民政府：", "recipient"),
        ("现将有关事项通知如下，请结合实际认真贯彻执行。", "body"),
        ("重点工作包括：一是加强组织领导；二是细化任务分工；三是强化督导落实。", "body"),
        ("示例单位", "signature"),
        ("2026年9月11日", "date"),
    ]
    return DocumentModel(
        metadata=meta,
        paragraphs=[Paragraph(index=i, text=t, role=r) for i, (t, r) in enumerate(texts)],
    )


def generate_golden(doc_type: str, out_path: str | Path) -> Path:
    """生成黄金样本 docx 并返回路径。"""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    return generate_docx(golden_model(doc_type), out)


def build_baseline(docx_path: str | Path, out_dir: str | Path) -> dict:
    """为黄金样本生成基线：docx sha256 + 每页感知哈希。无渲染环境时仅记录 sha256。"""
    docx = Path(docx_path)
    baseline = {"docx_sha256": file_sha256(docx), "pages": [], "renderable": False}
    pngs = doc_to_pngs(docx, out_dir)
    if not pngs:
        return baseline
    baseline["renderable"] = True
    for p in pngs:
        baseline["pages"].append({"file": p.name, "ahash": image_average_hash(p)})
    return baseline


def compare_baselines(left: dict, right: dict) -> dict:
    """对比两份基线，返回逐页汉明距离与总体结果。"""
    pages = []
    total_distance = 0
    for i, (a, b) in enumerate(zip(left.get("pages", []), right.get("pages", [])), start=1):
        d = hash_distance(int(a.get("ahash", 0)), int(b.get("ahash", 0)))
        total_distance += d
        pages.append({"page": i, "distance": d, "pass": d <= 12})
    same_doc = left.get("docx_sha256") == right.get("docx_sha256")
    return {
        "same_docx": same_doc,
        "pages": pages,
        "total_distance": total_distance,
        "renderable": bool(left.get("renderable")) and bool(right.get("renderable")),
        "pass": same_doc and (total_distance == 0 or all(p["pass"] for p in pages)) if pages else same_doc,
    }