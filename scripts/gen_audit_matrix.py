# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""
生成《GB/T 9704-2012 标准证据矩阵》文档（原创实现）。

依据规则目录中的 YAML 文件，为每个文种生成：
  - 检查规则表（含标准条款依据 standard_ref）
  - 修复规则表（经 ref_check / target 关联条款）
  - 规则统计汇总（用于 README 口径统一）

用法（项目根目录）：
  python scripts/gen_audit_matrix.py [--out docs/gbt9704-audit-matrix.md]
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# 使 backend 包可导入
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from core.rules.loader import list_available_types  # noqa: E402
from core.rules.manager import load_rules_merged  # noqa: E402
from core.rules.standard_refs import resolve_standard_ref, standard_ref_note  # noqa: E402

OUT_DEFAULT = Path(__file__).resolve().parent.parent / "docs" / "gbt9704-audit-matrix.md"

TYPE_NAMES = {
    "notice": "通知",
    "report": "报告",
    "request": "请示",
    "reply": "批复",
    "meeting": "会议纪要",
    "decision": "决定",
    "resolution": "决议",
    "announcement": "公告",
    "bill": "通告",
    "bulletin": "公报",
    "command": "命令（令）",
    "instruction": "意见",
    "letter": "函",
    "communique": "公报",
    "opinion": "意见",
    "regulation": "规定",
    "summary": "总结",
    "work_plan": "工作计划",
    "technical_proposal": "技术方案",
    "table_sign": "表格签章",
    "notice_public": "公示",
}


def _fix_clause(fix_rule: dict, check_rules: dict) -> str:
    """修复规则条款：优先按其 ref_check 关联的检查规则解析。"""
    ref = fix_rule.get("ref_check")
    if ref:
        rule = check_rules.get(ref)
        if rule:
            return resolve_standard_ref(rule)
    # 回退：按 target 字段推断
    target = fix_rule.get("target", "")
    field = {"title": "title.", "doc_title": "title.", "body": "body."}.get(target, "")
    return resolve_standard_ref({"field": field}) if field else ""


def build_matrix() -> str:
    lines: list[str] = []
    lines.append("# GB/T 9704-2012 标准证据矩阵")
    lines.append("")
    lines.append(
        "> 本矩阵由 `scripts/gen_audit_matrix.py` 依据规则 YAML 自动生成，"
        "将每条检查/修复规则关联到《党政机关公文格式》GB/T 9704-2012 对应条款，"
        "作为规则体系的标准依据证据链。"
    )
    lines.append("")
    lines.append("**统计口径说明**：规则条数为「公共基础层 + 文种层」合并去重后的生效条数。")
    lines.append("")

    types = list_available_types()
    summary_rows: list[tuple[str, int, int]] = []
    for doc_type in types:
        rules = load_rules_merged(doc_type)
        check_rules = {r.get("id"): r for r in rules.get("check_rules", []) if r.get("id")}
        fix_rules = rules.get("fix_rules", [])
        summary_rows.append((doc_type, len(check_rules), len(fix_rules)))

        name = TYPE_NAMES.get(doc_type, doc_type)
        lines.append(f"## {doc_type}（{name}）")
        lines.append("")
        lines.append("### 检查规则")
        lines.append("")
        lines.append("| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |")
        lines.append("|---|---|---|---|---|---|")
        for rid in sorted(check_rules):
            r = check_rules[rid]
            clause = resolve_standard_ref(r)
            lines.append(
                f"| {rid} | {r.get('severity', '')} | {r.get('name', '')} | {clause or '—'} "
                f"| {r.get('field', '')} | {r.get('expected', '')} |"
            )
        lines.append("")
        lines.append("### 修复规则")
        lines.append("")
        lines.append("| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |")
        lines.append("|---|---|---|---|---|")
        for fr in fix_rules:
            rid = fr.get("id", "")
            lines.append(
                f"| {rid} | {fr.get('action', '')} | {fr.get('target', '')} "
                f"| {fr.get('ref_check', '—')} | {_fix_clause(fr, check_rules) or '—'} |"
            )
        lines.append("")

    lines.append("---")
    lines.append("## 规则统计汇总")
    lines.append("")
    lines.append("| 文种 | 检查规则 | 修复规则 |")
    lines.append("|---|---|---|")
    for doc_type, c, f_ in summary_rows:
        lines.append(f"| {doc_type}（{TYPE_NAMES.get(doc_type, '')}） | {c} | {f_} |")
    total_c = sum(c for _, c, _ in summary_rows)
    lines.append("")
    lines.append(
        f"合计：{len(types)} 个文种，合并前规则条目检查 {total_c} 条。"
        "实际生效数 = 公共基础层（_common.yaml）与该文种层合并后的并集。"
    )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="生成 GB/T 9704 标准证据矩阵")
    parser.add_argument("--out", type=str, default=str(OUT_DEFAULT), help="输出 Markdown 路径")
    args = parser.parse_args()

    doc = build_matrix()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    print(f"[audit-matrix] 已生成: {out} ({len(doc)} chars)")


if __name__ == "__main__":
    main()