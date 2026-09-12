# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""
文档要素语义校验（原创实现）。

在格式规则检查之外，对文号、成文日期、发文机关署名等要素做语义级校验，
发现规则引擎无法通过字段比对识别的"格式正确但语义错误"问题。
规则在 SEMANTIC_RULES 登记，便于审计与扩展。

条款依据（GB/T 9704-2012）：
  - 7.2.2 发文字号：由发文机关代字、年份、发文顺序号组成，年份用六角括号〔〕括入
  - 7.3.6 成文日期：用阿拉伯数字将年、月、日标全
  - 7.3.5 发文机关署名：署名应编排于成文日期之上
"""

from __future__ import annotations

import re

from core.document.models import DocumentModel
from core.rules.checker import CheckIssue

# 规则登记表（供审计矩阵与说明文档引用）
SEMANTIC_RULES: list[dict] = [
    {"id": "CHK-S001", "name": "文号格式校验", "severity": "P1", "check_type": "expression", "standard_ref": "7.2.2"},
    {"id": "CHK-S002", "name": "成文日期格式校验", "severity": "P1", "check_type": "expression", "standard_ref": "7.3.6"},
    {"id": "CHK-S003", "name": "成文日期合理性校验", "severity": "P2", "check_type": "expression", "standard_ref": "7.3.6"},
    {"id": "CHK-S004", "name": "发文机关署名完整性校验", "severity": "P2", "check_type": "expression", "standard_ref": "7.3.5"},
]

_REF_MAP = {r["id"]: r for r in SEMANTIC_RULES}

# 规范文号：六角括号内为 4 位年份，其外以「号」结尾的阿拉伯数字顺序号
_DOC_NO_RE = re.compile(r"〔([^〕]{1,20})〕(\d{1,4})号")
# 非规范括号的文号（如 [2026]1号、(2026)1号）
_BAD_BRACKET_RE = re.compile(r"[\(\[【]\s*(\d{1,4})\s*[\)\]】]\s*(\d{1,4})\s*号")
# 标准成文日期：阿拉伯数字年月日齐全
_DATE_FULL_RE = re.compile(r"(\d{4})年(\d{1,2})月(\d{1,2})日")
# 缺「日」的日期（向后否定，避免与完整日期误判）
_DATE_NO_DAY_RE = re.compile(r"(\d{4})年(\d{1,2})月(?!\d)")
# 非规范分隔日期（2026-09-11 / 2026.9.11 等）
_DATE_DASH_RE = re.compile(r"\d{4}[-/.]\d{1,2}[-/.]\d{1,2}")
# 中文数字日期（二〇二六年九月十一日）——公文规范要求阿拉伯数字
_DATE_CN_DIGIT_RE = re.compile(r"[〇零一二三四五六七八九十]{2,4}年[一二三四五六七八九十]{1,3}月")


def _new_issue(rule_id: str, location: str, original: str, fix: str, reason: str) -> CheckIssue:
    meta = _REF_MAP.get(rule_id, {})
    return CheckIssue(
        rule_id=rule_id,
        check_type=meta.get("check_type", "expression"),
        severity=meta.get("severity", "P2"),
        name=meta.get("name", rule_id),
        location=location,
        original_text=original,
        suggested_fix=fix,
        reason=reason,
        standard_ref=meta.get("standard_ref", ""),
    )


def _non_empty_texts(model: DocumentModel) -> list[tuple[int, str]]:
    """返回 (段落索引, 文本) 列表，跳过空段落与明显为标题的段落。"""
    result = []
    for p in model.paragraphs:
        text = (p.text or "").strip()
        if text and p.role not in ("title",):
            result.append((p.index, text))
    return result


def _check_doc_number(model: DocumentModel) -> list[CheckIssue]:
    issues: list[CheckIssue] = []
    for idx, text in _non_empty_texts(model):
        # 六角括号内年份位数错误
        for m in _DOC_NO_RE.finditer(text):
            year_part = m.group(1)
            digits = re.fullmatch(r"(\d{4})(.*)", year_part)
            if not digits:
                issues.append(
                    _new_issue(
                        "CHK-S001",
                        f"paragraph:{idx}",
                        m.group(0),
                        "例：××发〔2026〕1号",
                        f"文号年份应使用 4 位阿拉伯数字并用六角括号〔〕括入，当前为「{year_part}」",
                    )
                )
                continue
            serial = m.group(2)
            if serial.startswith("0"):
                issues.append(
                    _new_issue(
                        "CHK-S001",
                        f"paragraph:{idx}",
                        m.group(0),
                        f"例：……〔2026〕{int(serial)}号",
                        "发文顺序号前不应补零",
                    )
                )
        # 非规范括号
        for m in _BAD_BRACKET_RE.finditer(text):
            issues.append(
                _new_issue(
                    "CHK-S001",
                    f"paragraph:{idx}",
                    m.group(0),
                    "改为六角括号：××发〔2026〕1号",
                    "发文字号年份应使用六角括号〔〕，而不是中括号/圆括号",
                )
            )
    return issues


def _check_date(model: DocumentModel) -> list[CheckIssue]:
    issues: list[CheckIssue] = []
    for idx, text in _non_empty_texts(model):
        # 非规范分隔日期
        for m in _DATE_DASH_RE.finditer(text):
            issues.append(
                _new_issue(
                    "CHK-S002",
                    f"paragraph:{idx}",
                    m.group(0),
                    "改为「2026年9月11日」",
                    "成文日期应使用中文年月日全称写法（阿拉伯数字）",
                )
            )
        # 缺「日」
        for m in _DATE_NO_DAY_RE.finditer(text):
            if _DATE_FULL_RE.search(text, m.end()):
                continue
            issues.append(
                _new_issue(
                    "CHK-S002",
                    f"paragraph:{idx}",
                    m.group(0),
                    f"补全：{m.group(1)}年{m.group(2)}月X日",
                    "成文日期应标全年、月、日",
                )
            )
        # 中文数字日期
        for m in _DATE_CN_DIGIT_RE.finditer(text):
            issues.append(
                _new_issue(
                    "CHK-S002",
                    f"paragraph:{idx}",
                    m.group(0),
                    "使用阿拉伯数字（例：2026年9月11日）",
                    "成文日期应使用阿拉伯数字，而非中文数字",
                )
            )
        # 合理性：月 1-12、日 1-31；防止把物品编号误判（限定行角色或行首）
        for m in _DATE_FULL_RE.finditer(text):
            month, day = int(m.group(2)), int(m.group(3))
            if not (1 <= month <= 12 and 1 <= day <= 31):
                issues.append(
                    _new_issue(
                        "CHK-S003",
                        f"paragraph:{idx}",
                        m.group(0),
                        "修正为真实日期",
                        f"成文日期不合理：月 {month}、日 {day} 超出有效范围",
                    )
                )
    return issues


def _check_signature(model: DocumentModel) -> list[CheckIssue]:
    """日期存在时，检查其上方是否存在发文机关署名（短段落，非正文长句）。"""
    paras = model.paragraphs
    date_idx: int | None = None
    for i, p in enumerate(paras):
        text = (p.text or "").strip()
        if text and _DATE_FULL_RE.search(text) and len(text) <= 20:
            date_idx = i
            break

    if date_idx is None:
        return []

    # 向上寻找最近的非空段落
    sig_idx = None
    for i in range(date_idx - 1, max(-1, date_idx - 6), -1):
        if i < 0:
            break
        if (paras[i].text or "").strip():
            sig_idx = i
            break

    if sig_idx is None:
        return [
            _new_issue(
                "CHK-S004",
                f"paragraph:{date_idx}",
                paras[date_idx].text,
                "在成文日期上方补发文机关署名",
                "成文日期前未找到发文机关署名",
            )
        ]

    sig_text = paras[sig_idx].text.strip()
    if len(sig_text) > 50 or "。" in sig_text:
        return [
            _new_issue(
                "CHK-S004",
                f"paragraph:{sig_idx}",
                sig_text[:80],
                "署名应为机关（单位）全称或规范简称，紧排在成文日期上一行",
                "成文日期上方的段落疑似正文而非发文机关署名",
            )
        ]
    return []


def semantic_check(model: DocumentModel, doc_type: str | None = None) -> list[CheckIssue]:
    """对文档要素做语义级校验，返回 CheckIssue 列表（空文档安全）。"""
    if not model.paragraphs:
        return []
    issues: list[CheckIssue] = []
    issues.extend(_check_doc_number(model))
    issues.extend(_check_date(model))
    issues.extend(_check_signature(model))
    return issues