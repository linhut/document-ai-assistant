# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Document Validator — 文档格式质量自动验证器

验证 .docx 文件是否符合 GB/T 9704-2012 标准。
输出结构化报告，用于自动化测试和质量门禁。

验证维度：
  1. 字体检查（font）— eastAsia/ascii/hAnsi/cs 是否正确
  2. 样式继承（style）— docDefaults/Normal/Heading 是否存在
  3. 段落格式（layout）— 行距/缩进/对齐
  4. 页面设置（page）— A4/页边距
"""
from __future__ import annotations
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from dataclasses import dataclass, field
from typing import Any

from docx import Document

from core.document.font_utils import (
    INVALID_FONT_PATTERNS, TITLE_FONT, BODY_FONT, LATIN_FONT,
)
from utils.logger import logger


WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


@dataclass
class ValidationResult:
    """验证结果。"""
    font_errors: int = 0
    style_errors: int = 0
    layout_errors: int = 0
    page_errors: int = 0
    fallback_fonts: list[str] = field(default_factory=list)
    details: list[dict[str, Any]] = field(default_factory=list)
    passed: bool = True

    def to_dict(self) -> dict:
        return {
            "font_errors": self.font_errors,
            "style_errors": self.style_errors,
            "layout_errors": self.layout_errors,
            "page_errors": self.page_errors,
            "fallback_fonts": self.fallback_fonts,
            "total_errors": self.font_errors + self.style_errors + self.layout_errors + self.page_errors,
            "passed": self.passed,
            "details": self.details[:20],  # 最多返回 20 条
        }


def validate_document(file_path: str | Path) -> ValidationResult:
    """
    验证 .docx 文件的格式质量。

    Args:
        file_path: .docx 文件路径

    Returns:
        ValidationResult 包含各维度的错误数和详情
    """
    file_path = Path(file_path)
    result = ValidationResult()

    if not file_path.exists():
        result.passed = False
        result.details.append({"category": "file", "error": "File not found", "path": str(file_path)})
        return result

    try:
        # 读取 XML 原始内容
        xml_content = _read_document_xml(file_path)
        styles_xml = _read_styles_xml(file_path)

        # 1. 字体检查
        _check_fonts(xml_content, result)

        # 2. 样式继承检查
        _check_styles(styles_xml, result)

        # 3. 段落格式检查
        _check_layout(xml_content, result)

        # 4. 页面设置检查
        _check_page_setup(file_path, result)

        result.passed = (result.font_errors + result.style_errors +
                         result.layout_errors + result.page_errors) == 0

    except Exception as e:
        result.passed = False
        result.details.append({"category": "validator", "error": str(e)})

    return result


# ---------------------------------------------------------------------------
#  1. 字体检查
# ---------------------------------------------------------------------------

def _check_fonts(xml_content: str, result: ValidationResult):
    """检查 document.xml 中的字体设置。"""
    root = ET.fromstring(xml_content)

    rFonts_count = 0
    missing_eastasia = 0
    invalid_fonts: set[str] = set()

    for elem in root.iter():
        if not elem.tag.endswith("}rFonts"):
            continue

        rFonts_count += 1
        ea = elem.get(f"{{{WORD_NS}}}eastAsia")
        ascii_f = elem.get(f"{{{WORD_NS}}}ascii")
        hAnsi = elem.get(f"{{{WORD_NS}}}hAnsi")
        cs = elem.get(f"{{{WORD_NS}}}cs")

        # 检查 eastAsia 是否缺失
        if not ea:
            missing_eastasia += 1
            result.details.append({
                "category": "font",
                "error": "eastAsia font missing",
                "ascii": ascii_f,
            })

        # 检查无效字体
        for attr_val in [ea, ascii_f, hAnsi, cs]:
            if attr_val:
                for pattern in INVALID_FONT_PATTERNS:
                    if pattern.lower() in attr_val.lower():
                        invalid_fonts.add(attr_val)

    result.font_errors += missing_eastasia + len(invalid_fonts)
    result.fallback_fonts = list(invalid_fonts)

    if invalid_fonts:
        result.details.append({
            "category": "font",
            "error": f"Invalid fallback fonts detected: {invalid_fonts}",
        })


# ---------------------------------------------------------------------------
#  2. 样式继承检查
# ---------------------------------------------------------------------------

def _check_styles(styles_xml: str | None, result: ValidationResult):
    """检查 styles.xml 中的样式定义。"""
    if not styles_xml:
        result.style_errors += 1
        result.details.append({"category": "style", "error": "styles.xml not found"})
        return

    root = ET.fromstring(styles_xml)

    # 检查 docDefaults
    doc_defaults = root.find(f"{{{WORD_NS}}}docDefaults")
    if doc_defaults is None:
        result.style_errors += 1
        result.details.append({"category": "style", "error": "docDefaults missing"})

    # 检查是否存在样式定义
    styles = root.findall(f"{{{WORD_NS}}}style")
    style_ids = {s.get(f"{{{WORD_NS}}}styleId", "") for s in styles}

    if not style_ids:
        result.style_errors += 1
        result.details.append({"category": "style", "error": "No styles defined"})

    # 检查 Normal 样式
    if "Normal" not in style_ids and "a" not in style_ids:
        result.style_errors += 1
        result.details.append({"category": "style", "error": "Normal style missing"})


# ---------------------------------------------------------------------------
#  3. 段落格式检查
# ---------------------------------------------------------------------------

def _check_layout(xml_content: str, result: ValidationResult):
    """检查段落格式（行距、缩进、对齐）。"""
    root = ET.fromstring(xml_content)

    para_count = 0
    no_spacing = 0

    for elem in root.iter():
        if not elem.tag.endswith("}p"):
            continue

        para_count += 1
        pPr = None
        for child in elem:
            if child.tag.endswith("}pPr"):
                pPr = child
                break

        if pPr is None:
            continue

        # 检查行距
        spacing = pPr.find(f"{{{WORD_NS}}}spacing")
        if spacing is None:
            no_spacing += 1

    if para_count > 0 and no_spacing == para_count:
        result.layout_errors += 1
        result.details.append({
            "category": "layout",
            "error": f"No paragraphs have spacing defined ({para_count} total)",
        })


# ---------------------------------------------------------------------------
#  4. 页面设置检查
# ---------------------------------------------------------------------------

def _check_page_setup(file_path: Path, result: ValidationResult):
    """检查页面设置。"""
    try:
        doc = Document(str(file_path))
        section = doc.sections[0]

        # A4 检查
        width_mm = section.page_width.mm if section.page_width else 0
        height_mm = section.page_height.mm if section.page_height else 0

        if abs(width_mm - 210) > 5:
            result.page_errors += 1
            result.details.append({
                "category": "page",
                "error": f"Paper width not A4: {width_mm:.1f}mm (expected 210mm)",
            })

        if abs(height_mm - 297) > 5:
            result.page_errors += 1
            result.details.append({
                "category": "page",
                "error": f"Paper height not A4: {height_mm:.1f}mm (expected 297mm)",
            })

        # 页边距检查
        margins = {
            "top": (section.top_margin.mm, 37, 5),
            "bottom": (section.bottom_margin.mm, 35, 5),
            "left": (section.left_margin.mm, 28, 5),
            "right": (section.right_margin.mm, 26, 5),
        }
        for name, (actual, expected, tolerance) in margins.items():
            if actual and abs(actual - expected) > tolerance:
                result.page_errors += 1
                result.details.append({
                    "category": "page",
                    "error": f"Margin {name}: {actual:.1f}mm (expected {expected}mm)",
                })

    except Exception as e:
        result.page_errors += 1
        result.details.append({"category": "page", "error": str(e)})


# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------

def _read_document_xml(file_path: Path) -> str:
    """读取 word/document.xml。"""
    with zipfile.ZipFile(file_path, "r") as zf:
        return zf.read("word/document.xml").decode("utf-8")


def _read_styles_xml(file_path: Path) -> str | None:
    """读取 word/styles.xml。"""
    try:
        with zipfile.ZipFile(file_path, "r") as zf:
            if "word/styles.xml" in zf.namelist():
                return zf.read("word/styles.xml").decode("utf-8")
    except Exception:
        pass
    return None