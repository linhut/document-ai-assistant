# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Format checker: validates a DocumentModel against loaded rules.
Returns a list of CheckIssue objects.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from core.document.models import DocumentModel, Paragraph
from utils.logger import logger


@dataclass
class CheckIssue:
    """A single issue found during format checking."""
    rule_id: str
    check_type: str        # format / typo / expression / logic
    severity: str          # P0 / P1 / P2
    name: str
    location: str          # e.g. "paragraph:3"
    original_text: str = ""
    suggested_fix: str = ""
    reason: str = ""


def check_document(model: DocumentModel, rules: dict[str, Any]) -> list[CheckIssue]:
    """
    Run all check_rules from the rule set against the document model.

    Args:
        model: Parsed document model.
        rules: Merged rule dictionary (common + type-specific).

    Returns:
        List of CheckIssue instances.
    """
    issues: list[CheckIssue] = []
    check_rules = rules.get("check_rules", [])

    for rule in check_rules:
        rule_id = rule.get("id", "UNKNOWN")
        field_path = rule.get("field", "")
        expected = rule.get("expected")
        severity = rule.get("severity", "P2")
        name = rule.get("name", "")
        message = rule.get("message", "")

        # Dispatch based on field path prefix
        if field_path.startswith("heading_0.") or field_path.startswith("doc_title."):
            issues.extend(_check_heading_level(model, rule_id, severity, name, field_path, expected, message, level=0))
        elif field_path.startswith("heading_1."):
            issues.extend(_check_heading_level(model, rule_id, severity, name, field_path, expected, message, level=1))
        elif field_path.startswith("heading_2."):
            issues.extend(_check_heading_level(model, rule_id, severity, name, field_path, expected, message, level=2))
        elif field_path.startswith("heading_3."):
            issues.extend(_check_heading_level(model, rule_id, severity, name, field_path, expected, message, level=3))
        elif field_path.startswith("title."):
            issues.extend(_check_title(model, rule_id, severity, name, field_path, expected, message))
        elif field_path.startswith("body."):
            issues.extend(_check_body(model, rule_id, severity, name, field_path, expected, message))
        elif field_path.startswith("page_setup."):
            issues.extend(_check_page_setup(model, rule_id, severity, name, field_path, expected, message))
        elif field_path.startswith("signature.") or field_path.startswith("date."):
            issues.extend(_check_signature_area(model, rule_id, severity, name, field_path, expected, message, rules))
        else:
            # Generic check -- compare against rule's expected value at top level
            actual = _get_nested(rules, field_path)
            if actual is not None and str(actual) != str(expected):
                issues.append(CheckIssue(
                    rule_id=rule_id, check_type="format", severity=severity,
                    name=name, location="document",
                    original_text=str(actual), suggested_fix=str(expected),
                    reason=message,
                ))

    # Additional heuristic checks (not from YAML)
    issues.extend(_check_common_issues(model))

    logger.info(f"Check complete: {len(issues)} issues found")
    return issues


# ---------------------------------------------------------------------------
#  Sub-checkers
# ---------------------------------------------------------------------------

def _get_nested(d: dict, path: str) -> Any:
    """Traverse a nested dict by dot-separated path."""
    parts = path.split(".")
    current = d
    for p in parts:
        if isinstance(current, dict):
            current = current.get(p)
        else:
            return None
    return current


def _check_title(model, rule_id, severity, name, field_path, expected, message) -> list[CheckIssue]:
    """Check document main title paragraph formatting (heading_level=0)."""
    issues = []
    # Find main title: heading_level=0 first, fallback to heading_level=1
    headings = [p for p in model.paragraphs if p.is_heading and p.heading_level == 0]
    if not headings:
        headings = [p for p in model.paragraphs if p.is_heading and p.heading_level == 1]
    if not headings:
        # Check if first non-empty paragraph could be the title
        non_empty = [p for p in model.paragraphs if p.text.strip()]
        if non_empty:
            issues.append(CheckIssue(
                rule_id=rule_id, check_type="format", severity=severity,
                name=name, location="paragraph:0",
                original_text=non_empty[0].text[:80],
                suggested_fix="使用标题样式或设置方正小标宋简体字体",
                reason="未检测到公文标题（方正小标宋简体/居中22pt），请检查标题格式",
            ))
        return issues

    title_para = headings[0]
    sub_field = field_path.split(".", 1)[1] if "." in field_path else ""

    if sub_field == "font":
        for run in title_para.runs:
            if run.format.font_name and run.format.font_name != expected:
                issues.append(CheckIssue(
                    rule_id=rule_id, check_type="format", severity=severity,
                    name=name, location=f"paragraph:{title_para.index}",
                    original_text=run.format.font_name, suggested_fix=str(expected),
                    reason=message,
                ))
                break
    elif sub_field == "size":
        for run in title_para.runs:
            if run.format.font_size_pt and abs(run.format.font_size_pt - float(str(expected).replace("pt", ""))) > 0.5:
                issues.append(CheckIssue(
                    rule_id=rule_id, check_type="format", severity=severity,
                    name=name, location=f"paragraph:{title_para.index}",
                    original_text=f"{run.format.font_size_pt}pt",
                    suggested_fix=str(expected),
                    reason=message,
                ))
                break
    elif sub_field == "align":
        actual = title_para.format.alignment
        if actual and actual != str(expected).lower():
            issues.append(CheckIssue(
                rule_id=rule_id, check_type="format", severity=severity,
                name=name, location=f"paragraph:{title_para.index}",
                original_text=actual, suggested_fix=str(expected),
                reason=message,
            ))

    return issues


def _check_heading_level(model, rule_id, severity, name, field_path, expected, message, level: int) -> list[CheckIssue]:
    """
    检查指定级别的标题段落格式。

    Args:
        level: 标题级别 (0=公文大标题, 1=一级标题, 2=二级标题, 3=三级标题)
    """
    issues = []
    headings = [p for p in model.paragraphs if p.is_heading and p.heading_level == level]

    if not headings:
        # 对于 level 0 的大标题，尝试回退到第一个非空段落
        if level == 0:
            non_empty = [p for p in model.paragraphs if p.text.strip()]
            if non_empty:
                issues.append(CheckIssue(
                    rule_id=rule_id, check_type="format", severity=severity,
                    name=name, location=f"paragraph:{non_empty[0].index}",
                    original_text=non_empty[0].text[:80],
                    suggested_fix="使用标题样式或设置标题字体",
                    reason=f"未检测到{level}级标题",
                ))
        return issues

    sub_field = field_path.split(".", 1)[1] if "." in field_path else ""

    _NUMERIC_FIELDS = {"size", "line_spacing", "first_line_indent"}
    expected_val: float | None = None
    if expected and sub_field in _NUMERIC_FIELDS:
        try:
            exp_str = str(expected).strip()
            if "em" in exp_str:
                expected_val = float(exp_str.replace("em", "").strip()) * 16
            else:
                expected_val = float(exp_str.replace("pt", "").strip())
        except (ValueError, TypeError):
            pass

    # 检查该级别的所有标题段落
    for title_para in headings:

        if sub_field == "font":
            for run in title_para.runs:
                if run.format.font_name and run.format.font_name != expected:
                    issues.append(CheckIssue(
                        rule_id=rule_id, check_type="format", severity=severity,
                        name=name, location=f"paragraph:{title_para.index}",
                        original_text=run.format.font_name, suggested_fix=str(expected),
                        reason=message,
                    ))
                    break
        elif sub_field == "size":
            for run in title_para.runs:
                if run.format.font_size_pt and expected_val and abs(run.format.font_size_pt - expected_val) > 0.5:
                    issues.append(CheckIssue(
                        rule_id=rule_id, check_type="format", severity=severity,
                        name=name, location=f"paragraph:{title_para.index}",
                        original_text=f"{run.format.font_size_pt}pt",
                        suggested_fix=str(expected),
                        reason=message,
                    ))
                    break
        elif sub_field == "align":
            actual = title_para.format.alignment
            if actual and actual != str(expected).lower():
                issues.append(CheckIssue(
                    rule_id=rule_id, check_type="format", severity=severity,
                    name=name, location=f"paragraph:{title_para.index}",
                    original_text=actual, suggested_fix=str(expected),
                    reason=message,
                ))
        elif sub_field == "first_line_indent":
            if title_para.format.first_line_indent_pt is not None and expected_val:
                if abs(title_para.format.first_line_indent_pt - expected_val) > 4:
                    issues.append(CheckIssue(
                        rule_id=rule_id, check_type="format", severity=severity,
                        name=name, location=f"paragraph:{title_para.index}",
                        original_text=f"{title_para.format.first_line_indent_pt}pt",
                        suggested_fix=str(expected),
                        reason=message,
                    ))
        elif sub_field == "line_spacing":
            if title_para.format.line_spacing_pt and expected_val:
                if abs(title_para.format.line_spacing_pt - expected_val) > 1:
                    issues.append(CheckIssue(
                        rule_id=rule_id, check_type="format", severity=severity,
                        name=name, location=f"paragraph:{title_para.index}",
                        original_text=f"{title_para.format.line_spacing_pt}pt",
                        suggested_fix=str(expected),
                        reason=message,
                    ))

    return issues


def _check_body(model, rule_id, severity, name, field_path, expected, message) -> list[CheckIssue]:
    """Check body paragraph formatting (excluding signature/date)."""
    issues = []
    _EXCLUDE_ROLES = {'signature', 'date'}
    body_paras = [p for p in model.paragraphs
                  if not p.is_heading and p.text.strip() and p.role not in _EXCLUDE_ROLES]
    if not body_paras:
        return issues

    sub_field = field_path.split(".", 1)[1] if "." in field_path else ""

    # Only attempt numeric conversion for fields that expect numeric values.
    # Font fields pass a string like "仿宋_GB2312" which would crash float().
    _NUMERIC_FIELDS = {"size", "line_spacing", "first_line_indent"}
    expected_val: float | None = None
    if expected and sub_field in _NUMERIC_FIELDS:
        try:
            exp_str = str(expected).strip()
            if "em" in exp_str:
                # 1em = 16pt (公文字号基准，正文16pt)
                expected_val = float(exp_str.replace("em", "").strip()) * 16
            else:
                expected_val = float(exp_str.replace("pt", "").strip())
        except (ValueError, TypeError):
            logger.warning(f"Cannot convert expected value '{expected}' to float for field '{sub_field}'")

    for para in body_paras:  # Check ALL body paragraphs
        if sub_field == "font":
            for run in para.runs:
                if run.format.font_name and run.format.font_name != expected:
                    issues.append(CheckIssue(
                        rule_id=rule_id, check_type="format", severity=severity,
                        name=name, location=f"paragraph:{para.index}",
                        original_text=run.format.font_name, suggested_fix=str(expected),
                        reason=message,
                    ))
                    break
        elif sub_field == "size":
            for run in para.runs:
                if run.format.font_size_pt and expected_val and abs(run.format.font_size_pt - expected_val) > 0.5:
                    issues.append(CheckIssue(
                        rule_id=rule_id, check_type="format", severity=severity,
                        name=name, location=f"paragraph:{para.index}",
                        original_text=f"{run.format.font_size_pt}pt",
                        suggested_fix=str(expected),
                        reason=message,
                    ))
                    break
        elif sub_field == "line_spacing":
            if para.format.line_spacing_pt and expected_val:
                if abs(para.format.line_spacing_pt - expected_val) > 1:
                    issues.append(CheckIssue(
                        rule_id=rule_id, check_type="format", severity=severity,
                        name=name, location=f"paragraph:{para.index}",
                        original_text=f"{para.format.line_spacing_pt}pt",
                        suggested_fix=str(expected),
                        reason=message,
                    ))
        elif sub_field == "first_line_indent":
            if expected_val:
                if para.format.first_line_indent_pt is None:
                    # 未检测到首行缩进 — 视为格式缺失
                    issues.append(CheckIssue(
                        rule_id=rule_id, check_type="format", severity=severity,
                        name=name, location=f"paragraph:{para.index}",
                        original_text="无缩进",
                        suggested_fix=str(expected),
                        reason=f"正文首行缺少缩进（期望{expected}）",
                    ))
                elif abs(para.format.first_line_indent_pt - expected_val) > 4:
                    issues.append(CheckIssue(
                        rule_id=rule_id, check_type="format", severity=severity,
                        name=name, location=f"paragraph:{para.index}",
                        original_text=f"{para.format.first_line_indent_pt}pt",
                        suggested_fix=str(expected),
                        reason=message,
                    ))
        elif sub_field == "align":
            actual = para.format.alignment
            if actual and actual != str(expected).lower():
                issues.append(CheckIssue(
                    rule_id=rule_id, check_type="format", severity=severity,
                    name=name, location=f"paragraph:{para.index}",
                    original_text=actual, suggested_fix=str(expected),
                    reason=message,
                ))

    return issues


def _check_page_setup(model, rule_id, severity, name, field_path, expected, message) -> list[CheckIssue]:
    """Check page setup values."""
    issues = []
    sub_field = field_path.split(".", 1)[1] if "." in field_path else ""
    ps = model.page_setup

    field_map = {
        "margins.top": ("margin_top_mm", expected),
        "margins.bottom": ("margin_bottom_mm", expected),
        "margins.left": ("margin_left_mm", expected),
        "margins.right": ("margin_right_mm", expected),
        "paper_width_mm": ("paper_width_mm", expected),
        "paper_height_mm": ("paper_height_mm", expected),
    }

    if sub_field in field_map:
        attr_name, exp = field_map[sub_field]
        actual = getattr(ps, attr_name, None)
        if actual is not None and exp is not None:
            # 解析期望值为mm
            exp_str = str(exp).strip()
            try:
                if "cm" in exp_str:
                    exp_mm = float(exp_str.replace("cm", "").strip()) * 10
                elif "mm" in exp_str:
                    exp_mm = float(exp_str.replace("mm", "").strip())
                else:
                    exp_mm = float(exp_str)
            except (ValueError, TypeError):
                exp_mm = None
            if exp_mm is not None and abs(actual - exp_mm) > 2:
                issues.append(CheckIssue(
                    rule_id=rule_id, check_type="format", severity=severity,
                    name=name, location="page_setup",
                    original_text=f"{actual}mm", suggested_fix=str(expected),
                    reason=message,
                ))

    return issues


def _check_signature_area(model, rule_id, severity, name, field_path, expected, message, rules) -> list[CheckIssue]:
    """Check signature/date area formatting. Only check last 2 non-empty paragraphs (落款+日期)."""
    issues = []
    paras = [p for p in model.paragraphs if not p.is_heading and p.text.strip()]
    if not paras:
        return issues

    # Signature area: only last 2 paragraphs (落款单位 + 日期)
    sig_paras = paras[-2:] if len(paras) >= 2 else paras
    sub_field = field_path.split(".", 1)[1] if "." in field_path else ""

    for para in sig_paras:
        if sub_field == "align":
            if para.format.alignment and para.format.alignment != str(expected).lower():
                issues.append(CheckIssue(
                    rule_id=rule_id, check_type="format", severity=severity,
                    name=name, location=f"paragraph:{para.index}",
                    original_text=para.format.alignment, suggested_fix=str(expected),
                    reason=message,
                ))

    return issues


def _check_common_issues(model: DocumentModel) -> list[CheckIssue]:
    """Heuristic checks not driven by YAML rules."""
    issues = []

    for para in model.paragraphs:
        text = para.text

        # Extra spaces (2+ consecutive spaces)
        if "  " in text:
            issues.append(CheckIssue(
                rule_id="CHK-HEUR-001", check_type="format", severity="P1",
                name="多余空格",
                location=f"paragraph:{para.index}",
                original_text=text[:80],
                suggested_fix="移除多余空格",
                reason="段落中存在连续空格",
            ))

        # Extra blank lines (empty paragraphs)
        if not text.strip() and para.index > 0:
            prev = model.paragraphs[para.index - 1] if para.index - 1 < len(model.paragraphs) else None
            if prev and not prev.text.strip():
                issues.append(CheckIssue(
                    rule_id="CHK-HEUR-002", check_type="format", severity="P2",
                    name="多余空行",
                    location=f"paragraph:{para.index}",
                    original_text="(空行)",
                    suggested_fix="移除多余空行",
                    reason="连续出现多个空行",
                ))

    # --- 页码检查（GB/T 9704: 公文应标注页码）---
    has_page_num = False
    for footer in model.footers:
        if footer.has_page_number:
            has_page_num = True
            break
    if not has_page_num and model.footers:
        # 有页脚但没有检测到页码域
        issues.append(CheckIssue(
            rule_id="CHK-HEUR-004", check_type="format", severity="P1",
            name="页码检查",
            location="page_footer",
            original_text="未检测到页码",
            suggested_fix="在页脚中插入页码（半角阿拉伯数字）",
            reason="GB/T 9704要求公文标注页码，版心下边缘居中",
        ))

    return issues
