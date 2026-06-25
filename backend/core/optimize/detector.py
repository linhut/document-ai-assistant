# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Problem detector: higher-level analysis beyond basic rule checks.
Detects structural / semantic issues like inconsistent fonts, mixed styles, etc.
"""
from __future__ import annotations
from dataclasses import dataclass

from core.document.models import DocumentModel
from core.rules.checker import CheckIssue
from utils.logger import logger


def detect_inconsistencies(model: DocumentModel) -> list[CheckIssue]:
    """
    Detect inconsistencies across the whole document that
    per-rule checks might miss (e.g. mixed fonts in body).
    """
    issues: list[CheckIssue] = []

    # Collect fonts and sizes used in body paragraphs
    body_fonts: set[str] = set()
    body_sizes: set[float] = set()
    for para in model.paragraphs:
        if para.is_heading or not para.text.strip():
            continue
        for run in para.runs:
            if run.format.font_name:
                body_fonts.add(run.format.font_name)
            if run.format.font_size_pt:
                body_sizes.add(run.format.font_size_pt)

    if len(body_fonts) > 1:
        issues.append(CheckIssue(
            rule_id="CHK-DET-001", check_type="format", severity="P1",
            name="正文字体不统一",
            location="body",
            original_text=", ".join(sorted(body_fonts)),
            suggested_fix="统一使用一种正文字体",
            reason=f"正文中使用了 {len(body_fonts)} 种不同的字体",
        ))

    if len(body_sizes) > 1:
        issues.append(CheckIssue(
            rule_id="CHK-DET-002", check_type="format", severity="P1",
            name="正文字号不统一",
            location="body",
            original_text=", ".join(f"{s}pt" for s in sorted(body_sizes)),
            suggested_fix="统一使用一种正文字号",
            reason=f"正文中使用了 {len(body_sizes)} 种不同的字号",
        ))

    # Check heading hierarchy (no skip: 1 -> 3 without 2)
    prev_level = 0
    for para in model.paragraphs:
        if para.is_heading and para.heading_level:
            if prev_level > 0 and para.heading_level > prev_level + 1:
                issues.append(CheckIssue(
                    rule_id="CHK-DET-003", check_type="format", severity="P1",
                    name="标题层级跳跃",
                    location=f"paragraph:{para.index}",
                    original_text=para.text[:80],
                    suggested_fix=f"应使用 Heading {prev_level + 1}",
                    reason=f"标题从 H{prev_level} 直接跳到 H{para.heading_level}",
                ))
            prev_level = para.heading_level

    logger.info(f"Inconsistency detection: {len(issues)} issues")
    return issues
