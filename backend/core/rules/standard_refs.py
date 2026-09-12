# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""
GB/T 9704-2012 标准条款映射（证据链支撑，原创实现）

将检查规则字段路径映射到《党政机关公文格式》GB/T 9704-2012 的条款，
为每条规则提供可审计的标准依据。条款编号为标准公开事实信息；
本文件仅登记本项目规则实际涉及的条款，并保持独立可维护。

解析优先级：
  1. 规则 YAML 中显式声明的 `standard_ref` 字段；
  2. 按 `field` 前缀匹配 FIELD_REF_MAP；
  3. 均未命中时返回空字符串。
"""

from __future__ import annotations

from typing import Any

# 字段前缀 → (条款号, 标准要点)
FIELD_REF_MAP: dict[str, tuple[str, str]] = {
    "page_setup.": (
        "6.1",
        "页面要求：A4 纸张，页边距上 3.7cm、下 3.5cm、左 2.8cm、右 2.6cm，版心 156mm×225mm",
    ),
    "doc_title.": ("7.2.4", "标题：2 号小标宋体字，居中编排，回行时词意完整、排列对称"),
    "title.": ("7.2.4", "标题：2 号小标宋体字，居中编排"),
    "heading_0.": ("7.2.4", "标题层级：按一级标题格式编排"),
    "heading_1.": ("6.2", "一级标题：3 号黑体字"),
    "heading_2.": ("6.2", "二级标题：3 号楷体字"),
    "heading_3.": ("6.2", "三级标题：3 号仿宋体字加粗"),
    "body.": ("7.3.3", "正文：3 号仿宋体字，一般每面排 22 行、每行排 28 个字"),
    "signature.": ("7.3.5", "发文机关署名：编排于成文日期之上，以成文日期为准居中排"),
    "date.": ("7.3.6", "成文日期：用阿拉伯数字将年、月、日标全，右空四字编排"),
    "recipient.": ("7.2.5", "主送机关：编排于标题下空一行位置，顶格排，回行时仍顶格"),
    "attachment.": ("7.3.4", "附件说明：正文下空一行左空二字编排"),
    "cc.": ("7.4.1", "抄送机关：编排于版记中，4 号仿宋体字，左空一字"),
    "page_number.": ("7.4.2", "页码：4 号半角宋体阿拉伯数字，数字左右各放一条一字线"),
    "page_footer.": ("7.4.2", "页码：4 号半角宋体阿拉伯数字"),
    "line_spacing.": ("6.3", "行数和字数：一般每面排 22 行，行距固定值 28 磅"),
}


def resolve_standard_ref(rule: dict[str, Any]) -> str:
    """返回规则对应的标准条款号（显式声明优先，否则按字段解析）。"""
    explicit = rule.get("standard_ref")
    if explicit:
        return str(explicit)
    field = rule.get("field", "")
    for prefix, (clause, _note) in FIELD_REF_MAP.items():
        if field.startswith(prefix):
            return clause
    return ""


def standard_ref_note(field: str) -> str:
    """返回字段路径对应的标准要点说明（用于审计矩阵文档）。"""
    for prefix, (_clause, note) in FIELD_REF_MAP.items():
        if field.startswith(prefix):
            return note
    return ""
