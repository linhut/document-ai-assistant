# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""
视觉回归对比（原创实现）。

用法：
  python scripts/visual_regression/compare.py [--goldens tests/goldens] [--strict]
  --strict: 任一类型不通过时以非零退出码告警（默认 0，便于 CI 宽容处理）
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from vr_lib import GOLDEN_TYPES, build_baseline, compare_baselines

ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_GOLDENS = ROOT / "tests" / "goldens"


def main() -> None:
    parser = argparse.ArgumentParser(description="视觉回归对比")
    parser.add_argument("--goldens", type=str, default=str(DEFAULT_GOLDENS))
    parser.add_argument("--strict", action="store_true", help="失败时以非零码退出")
    args = parser.parse_args()

    goldens = Path(args.goldens)
    failed = []
    for doc_type in GOLDEN_TYPES:
        type_dir = goldens / doc_type
        baseline_file = type_dir / f"{doc_type}.baseline.json"
        if not baseline_file.exists():
            print(f"[compare] {doc_type}: 无基线，请先运行 generate_goldens.py")
            failed.append(doc_type)
            continue
        baseline = json.loads(baseline_file.read_text(encoding="utf-8"))
        docx = type_dir / f"{doc_type}.docx"
        current = build_baseline(docx, type_dir)
        result = compare_baselines(baseline, current)
        status = "PASS" if result["pass"] else "FAIL"
        print(
            f"[compare] {doc_type}: {status} "
            f"(same_docx={result['same_docx']} "
            f"pages={len(result['pages'])} total_distance={result['total_distance']})"
        )
        if not result["pass"]:
            failed.append(doc_type)

    if failed:
        print(f"[compare] 未通过: {', '.join(failed)}")
        if args.strict:
            sys.exit(1)
    else:
        print("[compare] 全部通过")


if __name__ == "__main__":
    main()