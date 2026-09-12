# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""
生成视觉回归黄金样本并建立基线（原创实现）。

用法：
  python scripts/visual_regression/generate_goldens.py [--out tests/goldens]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from vr_lib import GOLDEN_TYPES, build_baseline, generate_golden

ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUT = ROOT / "tests" / "goldens"


def main() -> None:
    parser = argparse.ArgumentParser(description="生成视觉回归黄金样本与基线")
    parser.add_argument("--out", type=str, default=str(DEFAULT_OUT))
    args = parser.parse_args()

    out = Path(args.out)
    results = []
    for doc_type in GOLDEN_TYPES:
        type_dir = out / doc_type
        type_dir.mkdir(parents=True, exist_ok=True)
        docx = generate_golden(doc_type, type_dir / f"{doc_type}.docx")
        baseline = build_baseline(docx, type_dir)
        baseline_file = type_dir / f"{doc_type}.baseline.json"
        baseline_file.write_text(
            json.dumps(baseline, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        results.append(
            {
                "type": doc_type,
                "docx": str(docx),
                "renderable": baseline["renderable"],
                "pages": len(baseline["pages"]),
                "baseline": str(baseline_file),
            }
        )
        print(
            f"[golden] {doc_type}: docx={docx.stat().st_size}B "
            f"renderable={baseline['renderable']} pages={len(baseline['pages'])}"
        )
    (out / "_summary.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[golden] 完成，共 {len(results)} 个黄金样本")


if __name__ == "__main__":
    main()