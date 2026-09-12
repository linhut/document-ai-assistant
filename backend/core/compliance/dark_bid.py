# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""
暗标 / 标书合规检查模块（原创实现）。

面向招投标场景（暗标/技术标）的合规扫描：
  1. 身份信息泄露（暗标一票否决项）：
     - 居民身份证号（GB 11643-1999 校验位验证，避免误报普通长数字）
     - 手机号
     - 电子邮箱
     - 银行卡号（16–19 位数字段）
  2. 异常标记：疑似单位名称/公章位置文字等（预留扩展点）

安全约定：所有命中的原文在输出中一律**脱敏**（身份证保留前 6 后 4、其余打码），
避免检查工具自身成为信息泄露渠道。
"""

from __future__ import annotations

import re

from core.document.models import DocumentModel
from core.rules.checker import CheckIssue

# 规则登记表
DARK_BID_RULES: list[dict] = [
    {"id": "DKB-C001", "name": "身份证号泄露", "severity": "P0", "check_type": "compliance"},
    {"id": "DKB-C002", "name": "手机号泄露", "severity": "P0", "check_type": "compliance"},
    {"id": "DKB-C003", "name": "电子邮箱泄露", "severity": "P1", "check_type": "compliance"},
    {"id": "DKB-C004", "name": "银行卡号泄露", "severity": "P1", "check_type": "compliance"},
]
_RULE_MAP = {r["id"]: r for r in DARK_BID_RULES}

_ID_RE = re.compile(r"(?<!\d)(\d{17}[\dXx])(?!\d)")
_MOBILE_RE = re.compile(r"(?<!\d)(1[3-9]\d{9})(?!\d)")
_EMAIL_RE = re.compile(r"(?<![A-Za-z0-9._%+-])([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})(?![A-Za-z0-9._%+-])")
_BANK_RE = re.compile(r"(?<!\d)(\d{16,19})(?!\d)")

# GB 11643 身份证校验
_WEIGHTS = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
_CHECK_MAP = ["1", "0", "X", "9", "8", "7", "6", "5", "4", "3", "2"]


def id_check_digit(id17: str) -> str:
    """计算 18 位身份证的校验位（GB 11643-1999）。"""
    total = sum(int(ch) * w for ch, w in zip(id17, _WEIGHTS))
    return _CHECK_MAP[total % 11]


def _valid_id(id18: str) -> bool:
    if not re.fullmatch(r"\d{17}[\dXx]", id18):
        return False
    return id_check_digit(id18[:17]) == id18[17].upper()


def _mask(text: str, found: str, kind: str) -> str:
    """对命中片段脱敏。身份证保留前 6 后 4，其余显示首尾各 2 位。"""
    if kind == "id":
        return found[:6] + "********" + found[-4:]
    if len(found) <= 6:
        return found[0] + "****"
    return found[:2] + "****" + found[-2:]


def _add_issue(issues: list[CheckIssue], rule_id: str, location: str, masked: str, text_ctx: str) -> None:
    meta = _RULE_MAP[rule_id]
    issues.append(
        CheckIssue(
            rule_id=rule_id,
            check_type=meta["check_type"],
            severity=meta["severity"],
            name=meta["name"],
            location=location,
            original_text=masked,
            suggested_fix=f"将「{masked}」替换为占位符或匿名化处理",
            reason=(
                "暗标评审要求不得出现可识别企业/个人的身份信息，"
                f"疑似泄露片段：{masked}（上下文：{text_ctx[:24]}…）"
            ),
            standard_ref="",
        )
    )


def _scan_text(text: str, location: str, issues: list[CheckIssue]) -> None:
    if not text:
        return
    # 身份证：先按校验位验证，避免误报普通长数字
    id_spans: list[tuple[int, int]] = []
    for m in _ID_RE.finditer(text):
        candidate = m.group(1)
        if _valid_id(candidate):
            _add_issue(issues, "DKB-C001", location, _mask(text, candidate, "id"), text)
            id_spans.append(m.span())
    # 手机号
    for m in _MOBILE_RE.finditer(text):
        _add_issue(issues, "DKB-C002", location, _mask(text, m.group(1), "mobile"), text)
    # 电子邮箱
    for m in _EMAIL_RE.finditer(text):
        _add_issue(issues, "DKB-C003", location, _mask(text, m.group(1), "email"), text)
    # 银行卡号（16–19 位数字段，且与已验证的身份证区间重叠时跳过，避免重复报）
    for m in _BANK_RE.finditer(text):
        if any(start < m.end() and m.start() < end for start, end in id_spans):
            continue
        _add_issue(issues, "DKB-C004", location, _mask(text, m.group(1), "bank"), text)


def dark_bid_check(model: DocumentModel) -> list[CheckIssue]:
    """对文档全文（正文段落 + 表格单元格）执行暗标合规扫描。"""
    issues: list[CheckIssue] = []
    for p in model.paragraphs:
        _scan_text(p.text or "", f"paragraph:{p.index}", issues)
    for t in model.tables:
        for c in t.cells:
            for cp in c.paragraphs:
                _scan_text(cp.text or "", f"table:{t.index}:cell({c.row},{c.col})", issues)
    return issues