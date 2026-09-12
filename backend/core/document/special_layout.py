# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""
特殊版式模块（原创实现）。

在文档生成阶段按 `DocumentMetadata.layout_profile` 应用特殊版式：

  - formal  正式发文（红头预印纸套打）：预留红头区域高度（37–130mm 可配置），
            并在标题前保留两行 28 磅版心空行；
  - letter  信函式：首页上端红色双线（上粗下细），末页版记下方底线（上细下粗）；
  - command 命令（令）式：令号区域下方空两行编排正文；
  - 联合行文  layout_options.joint_orgs：在版头按机关列表分行编排机关标志。

所有 XML 操作均为本项目原创实现，仅依赖 python-docx 的 oxml 能力。
"""

from __future__ import annotations

import logging
from typing import Any

from docx.oxml import OxmlElement
from docx.oxml.ns import qn

logger = logging.getLogger("official_doc_ai")

# 28 磅固定行距的物理高度（mm）：28pt * 0.3528 ≈ 9.88mm
_LINE_28PT_MM = 28 * 0.3528
# 红头预留高度有效范围（mm，GB/T 9704 版心常规范围）
RESERVE_MIN_MM = 37.0
RESERVE_MAX_MM = 130.0
DEFAULT_RESERVE_MM = 72.0
# 红线上方双线与标题之间保留的空行数
LINES_BEFORE_TITLE = 2

SUPPORTED_PROFILES = ("formal", "letter", "command")


def _set_exact_line_spacing(paragraph, pt: float) -> None:
    """设置段落固定值行距（twips = pt * 20）。"""
    pPr = paragraph._p.get_or_add_pPr()
    spacing = pPr.find(qn("w:spacing"))
    if spacing is None:
        spacing = OxmlElement("w:spacing")
        pPr.append(spacing)
    spacing.set(qn("w:line"), str(int(round(pt * 20))))
    spacing.set(qn("w:lineRule"), "exact")


def _add_pbdr(paragraph, top_sz: int, bottom_sz: int, color: str = "FF0000") -> None:
    """为段落添加上下边框（sz 单位为八分之一磅，1/8 pt）。"""
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    for side, sz in (("top", top_sz), ("bottom", bottom_sz)):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(sz))
        el.set(qn("w:space"), "1")
        el.set(qn("w:color"), color)
        pBdr.append(el)
    pPr.append(pBdr)


def _prepend_blank(doc, count: int, line_pt: float = 28.0, text: str = "") -> None:
    """在正文起始位置插入 count 个指定行距的空段落（保留 sectPr 在末尾）。"""
    body = doc._element.body
    sectPr = body.find(qn("w:sectPr"))
    anchor = None
    for child in list(body):
        if child is sectPr:
            break
        if child.tag == qn("w:p"):
            anchor = child
            break
    for _ in range(count):
        p = doc.add_paragraph(text)
        _set_exact_line_spacing(p, line_pt)
        if anchor is not None:
            anchor.addprevious(p._p)
        elif sectPr is not None:
            sectPr.addprevious(p._p)


def apply_letterhead_reserve(doc, reserve_top_mm: float = DEFAULT_RESERVE_MM) -> int:
    """
    红头预印纸套打：在正文起始处插入空行，占用预留红头区域。

    高度按 28 磅固定行距折算行数，另保留标题前两行 28 磅空行。
    返回插入的空行数。
    """
    mm = float(reserve_top_mm)
    mm = max(RESERVE_MIN_MM, min(RESERVE_MAX_MM, mm))
    lines = max(1, round(mm / _LINE_28PT_MM))
    _prepend_blank(doc, lines)
    _prepend_blank(doc, LINES_BEFORE_TITLE)
    logger.info("special_layout: letterhead reserve applied (%.1fmm, %d lines)", mm, lines)
    return lines + LINES_BEFORE_TITLE


def apply_letter_double_lines(doc) -> None:
    """
    信函式：首页上端红色双线（上粗 4pt / 下细 0.75pt），
    末页版记下方底线（上细 0.75pt / 下粗 4pt）。
    """
    sections = doc.sections
    if not sections:
        return
    # 首页上端双线：置于第一节页眉
    header = sections[0].header
    header.is_linked_to_previous = False
    p = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
    _add_pbdr(p, top_sz=32, bottom_sz=6)  # 32/8pt=4pt 粗线在上, 6/8pt=0.75pt 细线在下
    # 末页底线：置于末节页脚
    footer = sections[-1].footer
    footer.is_linked_to_previous = False
    p2 = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    _add_pbdr(p2, top_sz=6, bottom_sz=32)  # 细线在上, 粗线在下
    logger.info("special_layout: letter double lines applied")


def apply_command_spacing(doc) -> None:
    """命令（令）式：令号下方空两行再排正文（以 28 磅固定行距实现）。"""
    _prepend_blank(doc, 2)
    logger.info("special_layout: command spacing applied")


def apply_joint_nameplate(doc, orgs: list[str]) -> None:
    """
    联合行文：版头机关标志按主办机关在前、联署机关分行编排。
    使用红色小标宋，居中排列。
    """
    if not orgs:
        return
    for name in orgs:
        p = doc.add_paragraph()
        run = p.add_run(name)
        # 红色小标宋（OXML 直接设置，保证 Word/WPS 兼容）
        rPr = run._r.get_or_add_rPr()
        color = OxmlElement("w:color")
        color.set(qn("w:val"), "FF0000")
        rPr.append(color)
        rFonts = rPr.find(qn("w:rFonts"))
        if rFonts is None:
            rFonts = OxmlElement("w:rFonts")
            rPr.append(rFonts)
        rFonts.set(qn("w:eastAsia"), "方正小标宋简体")
        rFonts.set(qn("w:ascii"), "方正小标宋简体")
        rFonts.set(qn("w:hAnsi"), "方正小标宋简体")
        jc = OxmlElement("w:jc")
        jc.set(qn("w:val"), "center")
        p._p.get_or_add_pPr().append(jc)
        # 将机关标志段落移动到正文起始处（保留 sectPr 在末尾）
        sectPr = doc._element.body.find(qn("w:sectPr"))
        anchor = None
        for child in list(doc._element.body):
            if child.tag == qn("w:p"):
                anchor = child
                break
        if anchor is not None:
            anchor.addprevious(p._p)
        elif sectPr is not None:
            sectPr.addprevious(p._p)
    logger.info("special_layout: joint nameplate applied (%d orgs)", len(orgs))


def apply_layout_profile(doc, model) -> None:
    """按模型声明的版式档案应用特殊版式（无档案/未知档案时跳过档案项，联合行文独立生效）。"""
    profile = (model.metadata.layout_profile or "").strip().lower()
    options: dict[str, Any] = dict(model.metadata.layout_options or {})

    # 联合行文机关标志与档案无关，独立生效
    orgs = options.get("joint_orgs") or []
    if isinstance(orgs, list) and orgs:
        apply_joint_nameplate(doc, [str(o) for o in orgs])

    if profile not in SUPPORTED_PROFILES:
        return

    if profile == "formal":
        mm = options.get("reserve_top_mm", DEFAULT_RESERVE_MM)
        apply_letterhead_reserve(doc, float(mm or DEFAULT_RESERVE_MM))
    elif profile == "letter":
        apply_letter_double_lines(doc)
    elif profile == "command":
        apply_command_spacing(doc)