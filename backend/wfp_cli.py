#!/usr/bin/env python3
"""
(c) 2026 Jose AI (https://www.linhut.cn)
Licensed under the MIT License. See the LICENSE file for details.

公文文档优化器 CLI 接口

参考 Word-Formatter-Pro 的 CLI 架构，支持子命令：
- format: 格式化文档
- check: 检查文档格式
- optimize: 优化文档

用法：
  python wfp_cli.py format input.docx -o output.docx
  python wfp_cli.py check input.docx --doc-type notice
  python wfp_cli.py optimize input.docx --doc-type notice -o output.docx
"""
import argparse
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.logger import logger


def cmd_format(args):
    """格式化文档"""
    from core.document.parser import parse_docx
    from core.document.generator import generate_docx
    from core.rules.engine import RuleEngine

    engine = RuleEngine()
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path.with_stem(input_path.stem + '_formatted')

    try:
        model = parse_docx(str(input_path))
        doc_type = args.doc_type or 'notice'

        if args.apply_fixes:
            issues, fixed_model = engine.check_and_fix(model, doc_type, args.selected_rules.split(',') if args.selected_rules else None)
        else:
            issues = engine.check(model, doc_type)
            fixed_model = model

        generate_docx(fixed_model, str(output_path))
        print(f'格式化完成: {output_path} (修复 {len(issues)} 项)')
    except Exception as e:
        logger.error(f'格式化失败: {e}')
        sys.exit(1)


def cmd_check(args):
    """检查文档格式"""
    from core.document.parser import parse_docx
    from core.rules.engine import RuleEngine

    engine = RuleEngine()
    input_path = Path(args.input)
    doc_type = args.doc_type or 'notice'

    try:
        model = parse_docx(str(input_path))
        issues = engine.check(model, doc_type)

        if args.severity:
            issues = [i for i in issues if i.severity == args.severity]

        print(f'检查完成: {len(issues)} 个问题')
        for issue in issues:
            print(f'  [{issue.severity}] {issue.rule_id}: {issue.name} @ {issue.location}')
            print(f'    期望: {issue.suggested_fix}')
            print(f'    实际: {issue.original_text}')

        if args.json:
            import json
            results = [{
                'severity': i.severity, 'rule_id': i.rule_id, 'name': i.name,
                'location': i.location, 'original': i.original_text,
                'suggested': i.suggested_fix, 'reason': i.reason,
            } for i in issues]
            print(json.dumps(results, ensure_ascii=False, indent=2))

    except Exception as e:
        logger.error(f'检查失败: {e}')
        sys.exit(1)


def cmd_optimize(args):
    """优化文档"""
    from core.document.parser import parse_docx
    from core.document.generator import generate_docx
    from core.rules.engine import RuleEngine

    engine = RuleEngine()
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path.with_stem(input_path.stem + '_optimized')

    try:
        model = parse_docx(str(input_path))
        doc_type = args.doc_type or 'notice'
        issues, fixed_model = engine.check_and_fix(model, doc_type)

        generate_docx(fixed_model, str(output_path))

        p0 = sum(1 for i in issues if i.severity == 'P0')
        p1 = sum(1 for i in issues if i.severity == 'P1')
        p2 = sum(1 for i in issues if i.severity == 'P2')

        print(f'优化完成: {output_path}')
        print(f'  修复 {len(issues)} 项 (P0:{p0}, P1:{p1}, P2:{p2})')
    except Exception as e:
        logger.error(f'优化失败: {e}')
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='公文文档优化器 CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # format 子命令
    fmt_parser = subparsers.add_parser('format', help='格式化文档')
    fmt_parser.add_argument('input', help='输入文件路径')
    fmt_parser.add_argument('-o', '--output', help='输出文件路径')
    fmt_parser.add_argument('-t', '--doc-type', default='notice', help='文档类型 (默认: notice)')
    fmt_parser.add_argument('--apply-fixes', action='store_true', default=True, help='应用修复 (默认: True)')
    fmt_parser.add_argument('--selected-rules', help='仅应用指定规则ID，逗号分隔')
    fmt_parser.set_defaults(func=cmd_format)

    # check 子命令
    chk_parser = subparsers.add_parser('check', help='检查文档格式')
    chk_parser.add_argument('input', help='输入文件路径')
    chk_parser.add_argument('-t', '--doc-type', default='notice', help='文档类型')
    chk_parser.add_argument('-s', '--severity', choices=['P0', 'P1', 'P2'], help='仅显示指定严重级别')
    chk_parser.add_argument('--json', action='store_true', help='输出JSON格式')
    chk_parser.set_defaults(func=cmd_check)

    # optimize 子命令
    opt_parser = subparsers.add_parser('optimize', help='优化文档')
    opt_parser.add_argument('input', help='输入文件路径')
    opt_parser.add_argument('-o', '--output', help='输出文件路径')
    opt_parser.add_argument('-t', '--doc-type', default='notice', help='文档类型')
    opt_parser.set_defaults(func=cmd_optimize)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == '__main__':
    main()
