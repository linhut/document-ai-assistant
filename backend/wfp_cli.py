#!/usr/bin/env python3
# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""
公文文档优化器 CLI 接口

支持子命令：
- format: 格式化文档
- check: 检查文档格式
- optimize: 优化文档（支持版头/版记/页码注入，与桌面端行为一致）

用法：
  python wfp_cli.py format input.docx -o output.docx
  python wfp_cli.py check input.docx --doc-type notice
  python wfp_cli.py optimize input.docx --doc-type notice -o output.docx
  python wfp_cli.py optimize input.docx -o out.docx --header-config header.json --page-number-config page.json

配置 JSON 示例（header.json）：
  {"org_name": "XX市人民政府", "doc_number": "X政发〔2026〕1号", "signer": "张三"}
footer.json：
  {"cc": "市委办、市人大办", "printer": "XX市人民政府办公室", "print_date": "2026年9月26日"}
page.json：
  {"enabled": true, "font": "宋体", "size": 14, "alignment": "center", "format": "— {PAGE} —"}
"""

import argparse
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.logger import logger


def _load_json_config(path: str | None) -> dict | None:
    """加载 JSON 配置文件，缺失/非法时返回 None 并告警（不阻断主流程）。"""
    if not path:
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"跳过配置 {path}: {e}")
        return None


def _apply_layout(output_path: str, args) -> None:
    """将版头/版记/页码注入到已生成的文档（core.document.layout_injector）。"""
    from core.document.layout_injector import (
        _inject_header_to_docx,
        _inject_footer_to_docx,
        _inject_page_number_to_docx,
    )

    header_config = _load_json_config(getattr(args, "header_config", None))
    if header_config is None and getattr(args, "org_name", None):
        # 便捷参数兜底：--org-name/--doc-number/--signer
        header_config = {
            "org_name": args.org_name,
            "doc_number": getattr(args, "doc_number", "") or "",
            "signer": getattr(args, "signer", "") or "",
        }
    footer_config = _load_json_config(getattr(args, "footer_config", None))
    page_number_config = _load_json_config(getattr(args, "page_number_config", None))

    if header_config:
        _inject_header_to_docx(str(output_path), header_config)
    if footer_config:
        _inject_footer_to_docx(str(output_path), footer_config)
    if page_number_config and page_number_config.get("enabled", True):
        _inject_page_number_to_docx(str(output_path), page_number_config)

    injected = [k for k, v in (("版头", header_config), ("版记", footer_config), ("页码", page_number_config)) if v]
    if injected:
        print(f"  已注入: {'、'.join(injected)}")


def cmd_format(args):
    """格式化文档"""
    from core.document.parser import parse_docx
    from core.document.generator import generate_docx
    from core.rules.engine import RuleEngine

    engine = RuleEngine()
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path.with_stem(input_path.stem + "_formatted")

    try:
        model = parse_docx(str(input_path))
        doc_type = args.doc_type or "notice"

        if args.apply_fixes:
            issues, fixed_model = engine.check_and_fix(
                model, doc_type, args.selected_rules.split(",") if args.selected_rules else None
            )
        else:
            issues = engine.check(model, doc_type)
            fixed_model = model

        generate_docx(fixed_model, str(output_path))
        print(f"格式化完成: {output_path} (修复 {len(issues)} 项)")
    except Exception as e:
        logger.error(f"格式化失败: {e}")
        sys.exit(1)


def cmd_check(args):
    """检查文档格式"""
    from core.document.parser import parse_docx
    from core.rules.engine import RuleEngine

    engine = RuleEngine()
    input_path = Path(args.input)
    doc_type = args.doc_type or "notice"

    try:
        model = parse_docx(str(input_path))
        issues = engine.check(model, doc_type)

        if args.severity:
            issues = [i for i in issues if i.severity == args.severity]

        print(f"检查完成: {len(issues)} 个问题")
        for issue in issues:
            print(f"  [{issue.severity}] {issue.rule_id}: {issue.name} @ {issue.location}")
            print(f"    期望: {issue.suggested_fix}")
            print(f"    实际: {issue.original_text}")

        if args.json:
            import json

            results = [
                {
                    "severity": i.severity,
                    "rule_id": i.rule_id,
                    "name": i.name,
                    "location": i.location,
                    "original": i.original_text,
                    "suggested": i.suggested_fix,
                    "reason": i.reason,
                }
                for i in issues
            ]
            print(json.dumps(results, ensure_ascii=False, indent=2))

    except Exception as e:
        logger.error(f"检查失败: {e}")
        sys.exit(1)


def cmd_optimize(args):
    """优化文档（含版头/版记/页码注入）"""
    from core.document.parser import parse_docx
    from core.document.generator import generate_docx
    from core.rules.engine import RuleEngine

    engine = RuleEngine()
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path.with_stem(input_path.stem + "_optimized")

    try:
        model = parse_docx(str(input_path))
        doc_type = args.doc_type or "notice"
        issues, fixed_model = engine.check_and_fix(model, doc_type)

        generate_docx(fixed_model, str(output_path))

        # 版头/版记/页码注入（与桌面端 optimize 行为一致）
        _apply_layout(output_path, args)

        p0 = sum(1 for i in issues if i.severity == "P0")
        p1 = sum(1 for i in issues if i.severity == "P1")
        p2 = sum(1 for i in issues if i.severity == "P2")

        print(f"优化完成: {output_path}")
        print(f"  修复 {len(issues)} 项 (P0:{p0}, P1:{p1}, P2:{p2})")
    except Exception as e:
        logger.error(f"优化失败: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="公文文档优化器 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # format 子命令
    fmt_parser = subparsers.add_parser("format", help="格式化文档")
    fmt_parser.add_argument("input", help="输入文件路径")
    fmt_parser.add_argument("-o", "--output", help="输出文件路径")
    fmt_parser.add_argument("-t", "--doc-type", default="notice", help="文档类型 (默认: notice)")
    fmt_parser.add_argument(
        "--apply-fixes",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="应用修复 (默认: True；--no-apply-fixes 仅检查不修改)",
    )
    fmt_parser.add_argument("--selected-rules", help="仅应用指定规则ID，逗号分隔")
    fmt_parser.set_defaults(func=cmd_format)

    # check 子命令
    chk_parser = subparsers.add_parser("check", help="检查文档格式")
    chk_parser.add_argument("input", help="输入文件路径")
    chk_parser.add_argument("-t", "--doc-type", default="notice", help="文档类型")
    chk_parser.add_argument("-s", "--severity", choices=["P0", "P1", "P2"], help="仅显示指定严重级别")
    chk_parser.add_argument("--json", action="store_true", help="输出JSON格式")
    chk_parser.set_defaults(func=cmd_check)

    # optimize 子命令（含版头/版记/页码注入）
    opt_parser = subparsers.add_parser("optimize", help="优化文档（支持版头/版记/页码注入）")
    opt_parser.add_argument("input", help="输入文件路径")
    opt_parser.add_argument("-o", "--output", help="输出文件路径")
    opt_parser.add_argument("-t", "--doc-type", default="notice", help="文档类型")
    opt_parser.add_argument("--header-config", help="版头配置 JSON 文件路径")
    opt_parser.add_argument("--footer-config", help="版记配置 JSON 文件路径")
    opt_parser.add_argument("--page-number-config", help="页码配置 JSON 文件路径")
    # 便捷参数（未提供 --header-config 时使用）
    opt_parser.add_argument("--org-name", help="发文机关名称（便捷注入版头）")
    opt_parser.add_argument("--doc-number", help="发文字号（便捷注入版头）")
    opt_parser.add_argument("--signer", help="签发人（便捷注入版头）")
    opt_parser.set_defaults(func=cmd_optimize)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
