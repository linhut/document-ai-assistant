"""
Document modifier: the single source of truth for all DocumentModel mutations.

所有文档模型的修改操作必须经过此模块。
禁止在其他位置直接修改 DocumentModel 的属性。

职责：
- 字体修改（font, size）
- 段落格式（alignment, spacing, indentation）
- 页面设置（margins）
- 文本清理（extra spaces, blank lines）
- 自定义修改（AI/手动）

设计参考：
- MCP-Doc 的文档能力抽象思想
- AIPoliDoc 的文档修改器概念
"""
from __future__ import annotations
import copy
import re
from typing import Any

from core.document.models import DocumentModel, Paragraph, Run, ParagraphFormat
from utils.logger import logger


# ---------------------------------------------------------------------------
#  Target selector: 根据 target 字符串选中段落
# ---------------------------------------------------------------------------

def _select_paragraphs(model: DocumentModel, target: str) -> list[Paragraph]:
    """
    根据 target 字符串返回需要修改的段落列表。

    target 支持:
    - "title"      → 所有标题段落 (is_heading=True)
    - "doc_title"  → 公文大标题 (heading_level=0)
    - "heading_0"  → 同 doc_title
    - "heading_1"  → 一级标题 (heading_level=1)
    - "heading_2"  → 二级标题 (heading_level=2)
    - "heading_3"  → 三级标题 (heading_level=3)
    - "body"       → 所有非标题、非空、非签名段落
    - "signature"  → 最后2个非空段落（落款+日期）
    - "all"        → 所有段落
    """
    if target == "title":
        return [p for p in model.paragraphs if p.is_heading]
    elif target in ("doc_title", "heading_0"):
        return [p for p in model.paragraphs if p.is_heading and p.heading_level == 0]
    elif target == "heading_1":
        return [p for p in model.paragraphs if p.is_heading and p.heading_level == 1]
    elif target == "heading_2":
        return [p for p in model.paragraphs if p.is_heading and p.heading_level == 2]
    elif target == "heading_3":
        return [p for p in model.paragraphs if p.is_heading and p.heading_level == 3]
    elif target == "body":
        # 排除签名段落（最后2个非空段落）
        non_empty = [p for p in model.paragraphs if p.text.strip()]
        sig_set = set(id(p) for p in non_empty[-2:]) if len(non_empty) >= 2 else set()
        return [p for p in model.paragraphs
                if not p.is_heading and p.text.strip() and id(p) not in sig_set]
    elif target == "signature":
        non_empty = [p for p in model.paragraphs if p.text.strip()]
        return non_empty[-2:] if len(non_empty) >= 2 else non_empty
    elif target == "all":
        return list(model.paragraphs)
    else:
        logger.warning(f"Unknown target: {target}")
        return []


# ---------------------------------------------------------------------------
#  Single-operation modifiers
# ---------------------------------------------------------------------------

def modify_font(model: DocumentModel, target: str, font_name: str) -> None:
    """
    修改指定段落的所有 run 的字体名称。
    Note: 实际的 eastAsia XML 写入由 generator 的 set_run_font 完成。
    """
    if not font_name:
        return
    for para in _select_paragraphs(model, target):
        for run in para.runs:
            run.format.font_name = font_name


def modify_size(model: DocumentModel, target: str, size_pt: float | None) -> None:
    """修改指定段落的所有 run 的字号。"""
    if size_pt is None:
        return
    for para in _select_paragraphs(model, target):
        for run in para.runs:
            run.format.font_size_pt = size_pt


def modify_alignment(model: DocumentModel, target: str, alignment: str) -> None:
    """修改指定段落的对齐方式。"""
    alignment = alignment.lower()
    for para in _select_paragraphs(model, target):
        para.format.alignment = alignment


def modify_line_spacing(model: DocumentModel, target: str, spacing_pt: float | None) -> None:
    """修改指定段落的行距。"""
    if spacing_pt is None:
        return
    for para in _select_paragraphs(model, target):
        para.format.line_spacing_pt = spacing_pt


def modify_first_line_indent(model: DocumentModel, target: str, indent_pt: float | None) -> None:
    """修改指定段落的首行缩进。"""
    if indent_pt is None:
        return
    for para in _select_paragraphs(model, target):
        para.format.first_line_indent_pt = indent_pt


def modify_margins(model: DocumentModel, margins: dict[str, str | float]) -> None:
    """修改页边距。margins dict: {top, bottom, left, right}。"""
    ps = model.page_setup
    mapping = {
        "top": "margin_top_mm",
        "bottom": "margin_bottom_mm",
        "left": "margin_left_mm",
        "right": "margin_right_mm",
    }
    for key, attr in mapping.items():
        if key in margins:
            parsed = _parse_mm_value(margins[key])
            if parsed is not None:
                setattr(ps, attr, parsed)


def remove_extra_spaces(model: DocumentModel) -> None:
    """清除段落中的多余空格（连续2个以上空格压缩为1个）。"""
    for para in model.paragraphs:
        for run in para.runs:
            if run.text and '  ' in run.text:
                run.text = re.sub(r' {2,}', ' ', run.text)


def remove_extra_blank_lines(model: DocumentModel) -> None:
    """清除连续空行（连续的空段落）。"""
    to_remove: set[int] = set()
    for i, para in enumerate(model.paragraphs):
        if not para.text.strip() and i > 0:
            prev = model.paragraphs[i - 1]
            if not prev.text.strip():
                to_remove.add(i)

    for idx in sorted(to_remove, reverse=True):
        model.paragraphs.pop(idx)


def replace_paragraph_text(model: DocumentModel, para_index: int, new_text: str) -> None:
    """替换指定段落的文本。"""
    if 0 <= para_index < len(model.paragraphs):
        para = model.paragraphs[para_index]
        para.text = new_text
        if para.runs:
            para.runs[0].text = new_text
            for r in para.runs[1:]:
                r.text = ""


def set_paragraph_format_attr(model: DocumentModel, para_index: int,
                               attr: str, value: Any) -> None:
    """设置指定段落格式属性。"""
    if 0 <= para_index < len(model.paragraphs):
        para = model.paragraphs[para_index]
        if hasattr(para.format, attr):
            setattr(para.format, attr, value)


# ---------------------------------------------------------------------------
#  Batch apply: apply a list of modification dicts (AI / manual)
# ---------------------------------------------------------------------------

def apply_modifications(model: DocumentModel, modifications: list[dict]) -> DocumentModel:
    """
    批量应用修改列表。

    每个 modification dict 格式:
        type: "replace_text" | "set_format"
        location: "paragraph:N"
        value: new value
        attribute: (for set_format) 属性名
    """
    fixed = copy.deepcopy(model)

    for mod in modifications:
        mod_type = mod.get("type", "")
        location = mod.get("location", "")
        value = mod.get("value", "")
        para_idx = _extract_para_index(location)

        if para_idx is None:
            continue

        if mod_type == "replace_text":
            replace_paragraph_text(fixed, para_idx, value)
        elif mod_type == "set_format":
            attr = mod.get("attribute")
            if attr:
                set_paragraph_format_attr(fixed, para_idx, attr, value)

    logger.info(f"Applied {len(modifications)} custom modifications")
    return fixed


# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------

def _parse_mm_value(value: str | float | None) -> float | None:
    """Parse margin value like '3.7cm' or 37 to mm."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    value = str(value).strip()
    try:
        if "cm" in value:
            return float(value.replace("cm", "").strip()) * 10
        if "mm" in value:
            return float(value.replace("mm", "").strip())
        return float(value)
    except (ValueError, TypeError):
        logger.warning(f"无法解析 mm 值: {value!r}")
        return None


def _parse_pt_value(value: str | float | None) -> float | None:
    """Parse size/spacing value like '16pt' or 16 to pt."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace("pt", "").strip())
    except (ValueError, TypeError):
        logger.warning(f"无法解析 pt 值: {value!r}")
        return None


def _parse_indent_value(value: str | float | None) -> float | None:
    """Parse indent value like '2em' or '32pt' to pt."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    value = str(value).strip()
    try:
        if "em" in value:
            return float(value.replace("em", "").strip()) * 16
        return float(value.replace("pt", "").strip())
    except (ValueError, TypeError):
        logger.warning(f"无法解析 indent 值: {value!r}")
        return None


def _extract_para_index(location: str) -> int | None:
    """Extract paragraph index from 'paragraph:3'."""
    try:
        return int(location.split(":")[-1].split(",")[0])
    except (ValueError, IndexError):
        return None