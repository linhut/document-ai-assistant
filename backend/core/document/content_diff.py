# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""
保持版式的文本替换规划模块（原创实现）。

思路：对段落新旧文本求公共前缀/后缀，仅把"中间变更区"落到包含变更起点的
那个 run 上，其余 run 的文本与格式原样保留。这样 AI 润色、人工修订等
内容修改不会破坏段落的字体/加粗/字号等格式（run 级保持）。

本模块只做**纯计算**（规划），不修改模型；实际写入由
`core.document.modifier.apply_paragraph_edits` 执行（单一变更点）。
"""

from __future__ import annotations

from core.document.models import Paragraph


def common_prefix_len(a: str, b: str) -> int:
    """两个字符串公共前缀长度。"""
    i = 0
    while i < len(a) and i < len(b) and a[i] == b[i]:
        i += 1
    return i


def common_suffix_len(a: str, b: str, prefix: int) -> int:
    """公共后缀长度（不计入公共前缀部分）。"""
    i = 0
    while (
        i < len(a) - prefix and i < len(b) - prefix and a[len(a) - 1 - i] == b[len(b) - 1 - i]
    ):
        i += 1
    return i


def _run_at(offsets: list[tuple[object, int]], lengths: list[int], pos: int) -> int:
    """返回包含字符偏移 pos 的 run 下标；pos 落在边界时取后一个 run，越界取最后一个。"""
    for idx, (run, start) in enumerate(offsets):
        if start <= pos < start + lengths[idx]:
            return idx
    return len(offsets) - 1


def plan_run_updates(paragraph: Paragraph, new_text: str) -> dict[int, str]:
    """
    计算把段落文本替换为 new_text 时，各 run 的新文本。

    返回 {run_index: 该 run 的新文本}；未变化的 run 不出现。
    段落无 run 时返回 {-1: new_text}（特殊标记，由执行方落 paragraph.text）。
    """
    old = paragraph.text or ""
    runs = paragraph.runs
    if new_text == old:
        return {}
    if not runs:
        return {-1: new_text}

    prefix = common_prefix_len(old, new_text)
    suffix = common_suffix_len(old, new_text, prefix)
    # 旧文本中变更区间为 [prefix, len(old)-suffix)，新文本相应片断为 [prefix, len(new)-suffix)
    j_old = len(old) - suffix
    j_new = len(new_text) - suffix
    middle_new = new_text[prefix:j_new]

    lengths = [len(r.text or "") for r in runs]
    offsets: list[tuple[object, int]] = []
    pos = 0
    for r in runs:
        offsets.append((r, pos))
        pos += len(r.text or "")

    # 变更起点所在 run：在 [prefix, j_old) 的头部写入 middle_new
    head_idx = _run_at(offsets, lengths, prefix)
    head_start = offsets[head_idx][1]
    head_prefix = old[head_start:prefix] if prefix > head_start else ""

    tail_idx = _run_at(offsets, lengths, j_old)
    if tail_idx == head_idx:
        # 变更完全落在单个 run 内：前缀 + 新文本 + 保留该 run 的后缀
        updates = {head_idx: head_prefix + middle_new + old[j_old:]}
    else:
        # 头尾不同 run：头部写前缀+新文本，中间 run 清空，尾部保留后缀
        updates = {head_idx: head_prefix + middle_new}
        for idx in range(head_idx + 1, tail_idx):
            updates[idx] = ""
        updates[tail_idx] = old[j_old:]

    # 过滤未变化的 run（保持"仅返回变更"的语义）
    filtered: dict[int, str] = {}
    for idx, t in updates.items():
        if 0 <= idx < len(runs) and t == (runs[idx].text or ""):
            continue
        filtered[idx] = t
    return filtered