# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Document modifier: the single source of truth for all DocumentModel mutations.

所有文档模型的修改操作必须经过此模块。
禁止在其他位置直接修改 DocumentModel 的属性。

职责：
- 字体修改（font, size）
- 段落格式（alignment, spacing, indentation）
- 页面设置（margins）
- 文本清理（extra spaces, blank lines）
- 自定义修改（AI/手动）

设计参考：
- MCP-Doc 的文档能力抽象思想
- AIPoliDoc 的文档修改器概念
"""
from __future__ import annotations
import copy
import re
from typing import Any

from core.document.models import DocumentModel, Paragraph, Run, ParagraphFormat, RunFormat, Table, TableCell
from utils.logger import logger


# ---------------------------------------------------------------------------
#  Target selector: 根据 target 字符串选中段落
# ---------------------------------------------------------------------------

def _select_paragraphs(model: DocumentModel, target: str) -> list[Paragraph]:
    """
    根据 target 字符串返回需要修改的段落列表。

    target 支持:
    - "title"      → 所有标题段落 (is_heading=True)
    - "doc_title"  → 公文大标题 (heading_level=0)
    - "heading_0"  → 同 doc_title
    - "heading_1"  → 一级标题 (heading_level=1)
    - "heading_2"  → 二级标题 (heading_level=2)
    - "heading_3"  → 三级标题 (heading_level=3)
    - "body"       → 所有非标题、非空、非签名段落
    - "signature"  → 最后2个非空段落（落款+日期）
    - "all"        → 所有段落
    """
    if target == "title":
        return [p for p in model.paragraphs if p.is_heading]
    elif target in ("doc_title", "heading_0"):
        return [p for p in model.paragraphs if p.is_heading and p.heading_level == 0]
    elif target == "heading_1":
        return [p for p in model.paragraphs if p.is_heading and p.heading_level == 1]
    elif target == "heading_2":
        return [p for p in model.paragraphs if p.is_heading and p.heading_level == 2]
    elif target == "heading_3":
        return [p for p in model.paragraphs if p.is_heading and p.heading_level == 3]
    elif target == "body":
        # 优先使用 role 字段，回退到启发式
        role_body = [p for p in model.paragraphs if p.role == 'body']
        if role_body:
            return role_body
        # 回退：排除签名段落（最后2个非空段落）
        non_empty = [p for p in model.paragraphs if p.text.strip()]
        sig_set = set(id(p) for p in non_empty[-2:]) if len(non_empty) >= 2 else set()
        return [p for p in model.paragraphs
                if not p.is_heading and p.text.strip() and id(p) not in sig_set]
    elif target == "signature":
        # 优先使用 role 字段
        role_sig = [p for p in model.paragraphs if p.role in ('signature', 'date')]
        if role_sig:
            return role_sig
        non_empty = [p for p in model.paragraphs if p.text.strip()]
        return non_empty[-2:] if len(non_empty) >= 2 else non_empty
    elif target == "all":
        return list(model.paragraphs)
    else:
        logger.warning(f"Unknown target: {target}")
        return []


# ---------------------------------------------------------------------------
#  Single-operation modifiers
# ---------------------------------------------------------------------------

def modify_font(model: DocumentModel, target: str, font_name: str) -> None:
    """
    修改指定段落的字体名称。
    无论当前值是否为 None，统一设置为目标字体。
    """
    if not font_name:
        return
    for para in _select_paragraphs(model, target):
        for run in para.runs:
            if run.format.font_name != font_name:
                run.format.font_name = font_name


def modify_size(model: DocumentModel, target: str, size_pt: float | None) -> None:
    """修改指定段落的字号。无论当前值是否为 None，统一设置为目标字号。"""
    if size_pt is None:
        return
    for para in _select_paragraphs(model, target):
        for run in para.runs:
            if run.format.font_size_pt is None or abs(run.format.font_size_pt - size_pt) > 0.5:
                run.format.font_size_pt = size_pt


def modify_alignment(model: DocumentModel, target: str, alignment: str) -> None:
    """修改指定段落的对齐方式。无论当前值是否为 None，统一设置。"""
    alignment = alignment.lower()
    for para in _select_paragraphs(model, target):
        if para.format.alignment != alignment:
            para.format.alignment = alignment


def modify_line_spacing(model: DocumentModel, target: str, spacing_pt: float | None,
                        spacing_rule: str | None = None) -> None:
    """修改指定段落的行距。同时设置行距规则（exact/multiple）。"""
    if spacing_pt is None:
        return
    for para in _select_paragraphs(model, target):
        para.format.line_spacing_pt = spacing_pt
        if spacing_rule:
            para.format.line_spacing_rule = spacing_rule


def modify_first_line_indent(model: DocumentModel, target: str, indent_pt: float | None) -> None:
    """修改指定段落的首行缩进。"""
    if indent_pt is None:
        return
    for para in _select_paragraphs(model, target):
        para.format.first_line_indent_pt = indent_pt


def modify_bold(model: DocumentModel, target: str, bold: bool) -> None:
    """修改指定段落所有 run 的加粗状态。"""
    for para in _select_paragraphs(model, target):
        for run in para.runs:
            run.format.bold = bold


def modify_margins(model: DocumentModel, margins: dict[str, str | float]) -> None:
    """修改页边距。margins dict: {top, bottom, left, right}。"""
    ps = model.page_setup
    mapping = {
        "top": "margin_top_mm",
        "bottom": "margin_bottom_mm",
        "left": "margin_left_mm",
        "right": "margin_right_mm",
    }
    for key, attr in mapping.items():
        if key in margins:
            parsed = _parse_mm_value(margins[key])
            if parsed is not None:
                setattr(ps, attr, parsed)


def remove_extra_spaces(model: DocumentModel) -> None:
    """清除段落中的多余空格（连续2个以上空格压缩为1个）。"""
    for para in model.paragraphs:
        for run in para.runs:
            if run.text and '  ' in run.text:
                run.text = re.sub(r' {2,}', ' ', run.text)


def remove_extra_blank_lines(model: DocumentModel, mode: str = 'delete_single') -> None:
    """处理空行（参考 Word-Formatter-Pro 的三种模式）。

    Args:
        model: 文档模型
        mode: 空行处理模式
            - 'keep_all': 不改动任何空行
            - 'delete_single': 删除单个空行，多个空行保留至1个
            - 'keep_single': 保留单个空行，多个空行保留至1个
    """
    if mode == 'keep_all':
        return

    if mode == 'keep_single':
        # 保留单个空行，多个连续空行合并为1个
        to_remove: set[int] = set()
        blank_count = 0
        for i, para in enumerate(model.paragraphs):
            if not para.text.strip():
                blank_count += 1
                if blank_count > 1:
                    to_remove.add(i)
            else:
                blank_count = 0

        for idx in sorted(to_remove, reverse=True):
            model.paragraphs.pop(idx)
    else:
        # delete_single: 删除单个空行，多个空行保留至1个
        to_remove: set[int] = set()
        for i, para in enumerate(model.paragraphs):
            if not para.text.strip() and i > 0:
                prev = model.paragraphs[i - 1]
                if not prev.text.strip():
                    to_remove.add(i)

        for idx in sorted(to_remove, reverse=True):
            model.paragraphs.pop(idx)

    # 重新编号段落索引，保证连续性
    for i, p in enumerate(model.paragraphs):
        p.index = i


# 空行处理模式常量（参考 Word-Formatter-Pro）
BLANK_LINE_MODE_KEEP_ALL = 'keep_all'
BLANK_LINE_MODE_DELETE_SINGLE = 'delete_single'
BLANK_LINE_MODE_KEEP_SINGLE = 'keep_single'


def fix_bold_range(model: DocumentModel) -> int:
    """
    正文段落加粗范围修复：
    1. 有冒号/句号边界 → 仅首句加粗，后续取消
    2. 无边界但整段加粗 → 全部取消加粗
    """
    changes = 0
    _EXCLUDE_ROLES = {'signature', 'date'}
    _CLAUSE_RE = re.compile(r'[:：。、]')

    for para in model.paragraphs:
        if para.is_heading and para.heading_level is not None and para.heading_level <= 2:
            continue
        if para.role in _EXCLUDE_ROLES:
            continue
        if not para.text.strip() or len(para.text.strip()) <= 30:
            continue
        if not para.runs or not all(r.format.bold for r in para.runs if r.text.strip()):
            continue

        full_text = para.text
        m = _CLAUSE_RE.search(full_text)

        if not m:
            # 无边界 → 整段取消加粗
            for run in para.runs:
                run.format.bold = False
            changes += 1
            continue

        # 有边界 → 首句保持加粗，后续取消
        split_pos = m.end()
        char_count = 0
        # 先收集需要分裂的 run 位置和文本，再统一修改
        # 避免在迭代 runs 列表过程中插入新元素
        insertions: list[tuple[int, str, str]] = []  # [(run_index, first_part, second_part)]
        for run_idx, run in enumerate(para.runs):
            run_end = char_count + len(run.text)
            if run_end <= split_pos:
                pass  # 首句内，保持加粗
            elif char_count >= split_pos:
                run.format.bold = False
            else:
                split_in_run = split_pos - char_count
                first_part = run.text[:split_in_run]
                second_part = run.text[split_in_run:]
                insertions.append((run_idx, first_part, second_part))
            char_count = run_end

        # 按索引倒序执行分裂操作，避免索引偏移
        for run_idx, first_part, second_part in reversed(insertions):
            para.runs[run_idx].text = first_part
            from core.document.models import Run as _Run, RunFormat as _RF
            new_run = _Run(
                index=run_idx + 1,
                text=second_part,
                format=_RF(
                    font_name=para.runs[run_idx].format.font_name,
                    font_size_pt=para.runs[run_idx].format.font_size_pt,
                    bold=False,
                ),
            )
            para.runs.insert(run_idx + 1, new_run)

        changes += 1

    return changes


# ---------------------------------------------------------------------------
#  标点规范化（参考 GB/T 15834 标点符号用法）
# ---------------------------------------------------------------------------

# 半角→全角映射表（仅在中文语境中转换）
_PUNCT_MAP = {
    ',': '，',
    ':': '：',
    ';': '；',
    '?': '？',
    '!': '！',
    '(': '（',
    ')': '）',
    '[': '【',
    ']': '】',
}

# 句号特殊处理：仅在中文字符后转换 . → 。（避免破坏 URL、数字小数点）
_PERIOD_RE = re.compile(r'([一-鿿　-〿＀-￯])\.(?=[^\d]|$)')

# 中文标点后多余空格
_PUNCT_SPACE_RE = re.compile(r'([，。；：！？）】])\s{2,}')

# 中文标点前多余空格（逗号/句号前不应有空格）
_PUNCT_BEFORE_SPACE_RE = re.compile(r'\s+([，。；：！？])')


def normalize_punctuation(model: DocumentModel) -> int:
    """
    标点规范化：半角→全角，清理标点前后多余空格。
    对每个 run 单独处理，保持 run 级格式不丢失。
    返回总修改次数。
    """
    total_changes = 0
    for para in model.paragraphs:
        for run in para.runs:
            if not run.text:
                continue
            original = run.text
            text = run.text

            # 1. 半角标点→全角（逐字符处理，避免破坏英文/URL）
            result = []
            for i, ch in enumerate(text):
                if ch in _PUNCT_MAP:
                    # 判断上下文：如果前后都是 ASCII 字母数字，则不转换（保护英文环境）
                    prev_ch = text[i-1] if i > 0 else ''
                    next_ch = text[i+1] if i < len(text)-1 else ''
                    # 括号始终转换（中文文档中半角括号几乎总是错误的）
                    if ch in '()[]':
                        result.append(_PUNCT_MAP[ch])
                    # 逗号/冒号/分号等：如果不在纯英文环境中则转换
                    elif prev_ch.isascii() and next_ch.isascii() and prev_ch.strip() and next_ch.strip():
                        result.append(ch)  # 保留半角（可能是英文环境）
                    else:
                        result.append(_PUNCT_MAP[ch])
                else:
                    result.append(ch)
            text = ''.join(result)

            # 2. 句号：仅中文字符后转换
            text = _PERIOD_RE.sub(r'\1。', text)

            # 3. 清理中文标点后多余空格
            text = _PUNCT_SPACE_RE.sub(r'\1', text)

            # 4. 清理中文标点前多余空格
            text = _PUNCT_BEFORE_SPACE_RE.sub(r'\1', text)

            if text != original:
                changes = sum(1 for a, b in zip(original, text) if a != b)
                total_changes += changes
                run.text = text

    return total_changes


def normalize_heading_content(model: DocumentModel) -> int:
    """
    标题编号统一化：
    - 一级标题：1、→ 一、（阿拉伯数字转中文）
    - 二级标题：(一)→（一）（半角括号转全角）
    - 三级标题：1．→ 1.（全角句号转半角）
    - 四级标题：(1)→（1）（半角括号转全角）
    返回修改次数。
    """
    changes = 0
    for para in model.paragraphs:
        if not para.text.strip():
            continue
        text = para.text.strip()

        # 一级标题：1、xxx → 一、xxx
        m = re.match(r'^(\d+)[、，](.+)', text)
        if m and para.is_heading and (para.heading_level == 1 or para.heading_level is None):
            num = int(m.group(1))
            cn = _arabic_to_chinese(num)
            if cn:
                new_text = f'{cn}、{m.group(2)}'
                if new_text != text:
                    para.text = new_text
                    if para.runs:
                        para.runs[0].text = new_text
                        for r in para.runs[1:]:
                            r.text = ""
                    changes += 1
                continue

        # 二级标题：(一)xxx → （一）xxx
        m = re.match(r'^\(([一二三四五六七八九十]+)\)(.+)', text)
        if m:
            new_text = f'（{m.group(1)}）{m.group(2)}'
            if new_text != text:
                para.text = new_text
                if para.runs:
                    para.runs[0].text = new_text
                    for r in para.runs[1:]:
                        r.text = ""
                changes += 1
            continue

        # 三级标题：1．xxx → 1.xxx（全角句号→半角）
        m = re.match(r'^(\d+)[．。](.+)', text)
        if m:
            new_text = f'{m.group(1)}.{m.group(2)}'
            if new_text != text:
                para.text = new_text
                if para.runs:
                    para.runs[0].text = new_text
                    for r in para.runs[1:]:
                        r.text = ""
                changes += 1
            continue

        # 四级标题：(1)xxx → （1）xxx
        m = re.match(r'^\((\d+)\)(.+)', text)
        if m:
            new_text = f'（{m.group(1)}）{m.group(2)}'
            if new_text != text:
                para.text = new_text
                if para.runs:
                    para.runs[0].text = new_text
                    for r in para.runs[1:]:
                        r.text = ""
                changes += 1

    return changes


def _arabic_to_chinese(n: int) -> str:
    """阿拉伯数字转中文数字（1-99）。"""
    if n < 1 or n > 99:
        return ''
    digits = '零一二三四五六七八九十'
    if n <= 10:
        return digits[n]
    if n < 20:
        return f'十{digits[n % 10]}' if n % 10 else '十'
    tens = n // 10
    ones = n % 10
    result = f'{digits[tens]}十'
    if ones:
        result += digits[ones]
    return result


def replace_paragraph_text(model: DocumentModel, para_index: int, new_text: str) -> None:
    """替换指定段落的文本。"""
    if 0 <= para_index < len(model.paragraphs):
        para = model.paragraphs[para_index]
        para.text = new_text
        if para.runs:
            para.runs[0].text = new_text
            for r in para.runs[1:]:
                r.text = ""


# ---------------------------------------------------------------------------
#  Markdown 语法识别与转换（AI 生成内容直接粘贴到 Word 的场景）
# ---------------------------------------------------------------------------

# markdown 标题标记：行首的 # ## ### #### 等，捕获 # 数量和正文
_MD_HEADING_RE = re.compile(r'^(#{1,6})\s+(.*)')

# markdown 加粗标记 **text** 和 __text__（不含斜体 *text* 避免误伤）
_MD_BOLD_RE = re.compile(r'\*{2}(.+?)\*{2}')
_MD_BOLD_UNDER_RE = re.compile(r'__(.+?)__')

# markdown 行首无序列表标记：- * +
_MD_UL_RE = re.compile(r'^[-*+]\s+')

# markdown 有序列表前缀：1. 2. 3. 或 1、2、3、
_MD_OL_RE = re.compile(r'^\d+[.、]\s*')

# markdown 表格行
_MD_TABLE_RE = re.compile(r'^\|.+\|.+\|$')

# markdown 表格分隔行：|----|----|
_MD_TABLE_SEP_RE = re.compile(r'^\|[\s\-:|]+\|$')

# markdown 水平分隔线：--- *** ___
_MD_HR_RE = re.compile(r'^[-*_]{3,}$')

# HTML 标签
_HTML_TAG_RE = re.compile(r'<[^>]+>')

# markdown 链接：[text](url)
_MD_LINK_RE = re.compile(r'\[([^\]]+)\]\([^)]+\)')

# 代码块标记 ```
_MD_CODE_BLOCK_RE = re.compile(r'^`{3,}')

# 行内代码 `code`
_MD_INLINE_CODE_RE = re.compile(r'`([^`]+)`')


def convert_markdown(model: DocumentModel) -> int:
    """
    识别 Markdown 格式标记并转换为对应的 Word 格式属性。

    转换规则：
    - # 标题     → heading_level=0, 方正小标宋 22pt 居中（公文标题）
    - ## 一、    → heading_level=1, 黑体 16pt（一级标题）
    - ### （一）  → heading_level=2, 楷体 16pt（二级标题）
    - #### 1.    → heading_level=3, 仿宋 16pt 加粗（三级标题）
    - **文字**   → bold=True（加粗）
    - - 列表     → 保留，添加左缩进
    - | 表格 |   → 转为真正的 Word Table 对象
    - ---        → 删除（分隔线）
    - <br>       → 删除（HTML标签）
    - [text](url) → 保留 text

    返回修改次数。
    """
    changes = 0

    # === 第一步：识别并提取 markdown 表格 ===
    # 连续的 |...| 行构成一个表格，|----| 为分隔行（跳过）
    table_regions = _detect_md_table_regions(model.paragraphs)
    table_para_indices = set()
    # 记录每个表格在原文档中的位置（原始段落索引），删除后需要调整
    table_insert_positions = []  # [(original_insert_after, Table对象)]

    for region in table_regions:
        header_cells = region['header']
        data_rows = region['rows']
        insert_idx = region['insert_after']  # 在这个段落索引之后插入表格

        if not header_cells:
            continue

        # 构建 Table 对象
        num_rows = 1 + len(data_rows)  # header + data
        num_cols = len(header_cells)
        table = Table(
            index=len(model.tables),
            rows=num_rows,
            cols=num_cols,
            cells=[],
        )

        # 填充表头单元格
        for col_idx, cell_text in enumerate(header_cells):
            cell_para = Paragraph(
                index=0, text=cell_text, is_heading=False,
                runs=[Run(index=0, text=cell_text, format=RunFormat(
                    font_name='黑体', font_size_pt=12, bold=True,
                ))],
                format=ParagraphFormat(alignment='center'),
            )
            table.cells.append(TableCell(row=0, col=col_idx, text=cell_text, paragraphs=[cell_para]))

        # 填充数据行单元格
        for row_idx, row_cells in enumerate(data_rows):
            for col_idx in range(num_cols):
                cell_text = row_cells[col_idx] if col_idx < len(row_cells) else ''
                # 清理加粗标记
                clean_bold = False
                if '**' in cell_text:
                    cell_text = _MD_BOLD_RE.sub(r'\1', cell_text)
                    cell_text = _MD_BOLD_UNDER_RE.sub(r'\1', cell_text)
                    clean_bold = True
                cell_text = _HTML_TAG_RE.sub('', cell_text).strip()

                cell_para = Paragraph(
                    index=0, text=cell_text, is_heading=False,
                    runs=[Run(index=0, text=cell_text, format=RunFormat(
                        font_name='仿宋_GB2312', font_size_pt=12,
                        bold=True if clean_bold else None,
                    ))],
                    format=ParagraphFormat(alignment='left'),
                )
                table.cells.append(TableCell(row=row_idx + 1, col=col_idx, text=cell_text, paragraphs=[cell_para]))

        model.tables.append(table)
        table_insert_positions.append((insert_idx, table))

        # 标记所有表格段落为待删除
        for idx in region['all_indices']:
            table_para_indices.add(idx)

        changes += 1

    # === 第二步：处理非表格段落的 markdown 语法 ===
    to_remove: list[int] = []

    for i, para in enumerate(model.paragraphs):
        # 跳过已标记为表格的段落
        if i in table_para_indices:
            to_remove.append(i)
            continue

        original_text = para.text
        if not original_text or not original_text.strip():
            continue

        text = para.text.strip()

        # --- 删除无用行 ---

        # 水平分隔线 --- *** ___
        if _MD_HR_RE.match(text):
            to_remove.append(i)
            continue

        # 代码块标记 ```
        if _MD_CODE_BLOCK_RE.match(text):
            to_remove.append(i)
            continue

        # --- 识别标题级别并设置格式 ---

        heading_match = _MD_HEADING_RE.match(text)
        if heading_match:
            level = len(heading_match.group(1))
            content = heading_match.group(2).strip()
            text = content

            if level == 1:
                para.is_heading = True
                para.heading_level = 0
                para.role = 'title'
                _apply_heading_format(para, content,
                    font='方正小标宋简体', size=22, align='center', bold=False)
            elif level == 2:
                para.is_heading = True
                para.heading_level = 1
                _apply_heading_format(para, content,
                    font='黑体', size=16, align='left', bold=False)
            elif level == 3:
                para.is_heading = True
                para.heading_level = 2
                _apply_heading_format(para, content,
                    font='楷体_GB2312', size=16, align='left', bold=False)
            elif level >= 4:
                para.is_heading = True
                para.heading_level = 3
                _apply_heading_format(para, content,
                    font='仿宋_GB2312', size=16, align='left', bold=True)

            changes += 1

        # --- 识别加粗标记 **text** ---

        has_bold = False
        if _MD_BOLD_RE.search(text) or _MD_BOLD_UNDER_RE.search(text):
            has_bold = True
            text = _MD_BOLD_RE.sub(r'\1', text)
            text = _MD_BOLD_UNDER_RE.sub(r'\1', text)

        # --- 清理其他 markdown 语法 ---

        text = _MD_LINK_RE.sub(r'\1', text)
        text = _MD_INLINE_CODE_RE.sub(r'\1', text)
        text = _HTML_TAG_RE.sub('', text)

        # --- 处理列表标记 ---

        is_list = False
        list_indent_pt = 0

        ul_match = _MD_UL_RE.match(text)
        if ul_match:
            is_list = True
            text = _MD_UL_RE.sub('', text)
            list_indent_pt = 32  # 2字符缩进

        ol_match = _MD_OL_RE.match(text)
        if ol_match and not para.is_heading:
            is_list = True

        # --- 应用格式修改到 run ---

        text = re.sub(r' {2,}', ' ', text).strip()

        if text != original_text or has_bold or is_list:
            para.text = text
            if para.runs:
                para.runs[0].text = text
                for r in para.runs[1:]:
                    r.text = ""

                if has_bold and not para.is_heading:
                    for r in para.runs:
                        r.format.bold = True

                if is_list and list_indent_pt > 0 and not para.is_heading:
                    para.format.left_indent_pt = list_indent_pt

            changes += 1

    # 删除标记为移除的段落（倒序）
    if to_remove:
        sorted_remove = sorted(to_remove, reverse=True)
        for idx in sorted_remove:
            model.paragraphs.pop(idx)
        # 重新编号段落索引
        for i, p in enumerate(model.paragraphs):
            p.index = i
        # 调整表格的 insert_after_index（扣除被删除的段落数）
        removed_sorted = sorted(to_remove)  # 升序
        for orig_idx, tbl in table_insert_positions:
            if orig_idx < 0:
                tbl.insert_after_index = -1
            else:
                # 计算 orig_idx 之前被删除了多少个段落
                removed_before = sum(1 for r in removed_sorted if r <= orig_idx)
                adjusted = orig_idx - removed_before
                # 确保不超过当前段落列表范围
                tbl.insert_after_index = min(adjusted, len(model.paragraphs) - 1)
        changes += 1  # 统一计为 1 次批量删除

    # === 第三步：内联标题分割（参考 Word-Formatter-Pro）===
    # 当标题和正文在同一段落中时自动拆分
    _split_inline_headings(model)

    return changes


def _split_inline_headings(model: DocumentModel) -> None:
    """内联标题分割：当标题和正文在同一段落中时自动拆分。

    参考 Word-Formatter-Pro 的实现：
    - 标题段落中包含"。"且后面紧跟正文时，自动拆分为标题+正文两个段落
    - 例如："关于XX的通知。各有关单位：为贯彻落实..."
    → 标题: "关于XX的通知"
    → 正文: "各有关单位：为贯彻落实..."
    """
    # 正则匹配标题+正文在同一段落的情况
    # 模式：标题文本（以。或；结尾）+ 正文文本
    inline_pattern = re.compile(
        r'^(.{2,60}[。；])\s*(.{4,}.*)$', re.DOTALL
    )

    insertions = []
    for i, para in enumerate(model.paragraphs):
        text = para.text.strip()
        if not text or para.is_heading:
            continue

        match = inline_pattern.match(text)
        if match:
            title_text = match.group(1).strip()
            body_text = match.group(2).strip()

            # 确保标题文本确实像一个标题（包含标题关键词）
            title_keywords = [
                "关于", "通知", "请示", "报告", "函", "纪要", "决定", "通告", "公告",
                "的意见", "的方案", "的办法", "的规定", "的决定", "的通知"
            ]
            is_likely_title = any(kw in title_text for kw in title_keywords)

            if is_likely_title and len(title_text) >= 4:
                insertions.append((i, title_text, body_text))

    # 执行拆分（从后往前，避免索引偏移）
    for i, title_text, body_text in reversed(insertions):
        # 创建标题段落
        title_para = Paragraph(
            index=i, text=title_text, is_heading=True, heading_level=0, role='title',
            runs=[Run(index=0, text=title_text, format=RunFormat(
                font_name='方正小标宋简体', font_size_pt=22,
            ))],
            format=ParagraphFormat(alignment='center', line_spacing_pt=33.0),
        )

        # 创建正文段落
        body_para = Paragraph(
            index=i + 1, text=body_text, is_heading=False, heading_level=None, role='body',
            runs=[Run(index=0, text=body_text, format=RunFormat(
                font_name='仿宋_GB2312', font_size_pt=16,
            ))],
            format=ParagraphFormat(
                alignment='justify', line_spacing_pt=28.95, first_line_indent_pt=32.0,
            ),
        )

        # 替换原段落为两个新段落
        model.paragraphs[i] = title_para
        model.paragraphs.insert(i + 1, body_para)

    # 重新编号
    for i, p in enumerate(model.paragraphs):
        p.index = i


# --- 附件标记正则 ---
RE_ATTACHMENT = re.compile(r'^\s*附件[：:1-9]?\s*(?:说明|清单|内容)?')


def _add_attachment_page_breaks(model: DocumentModel) -> None:
    """在附件标记段落前添加分页标记。

    参考 Word-Formatter-Pro 的实现：
    - 检测 "附件"、"附件1"、"附件：" 等模式
    - 在附件前设置分页标记（通过 paragraph 前缀标记）
    - 附件标题和副标题保持原有格式
    """
    for i, para in enumerate(model.paragraphs):
        text = para.text.strip()
        if RE_ATTACHMENT.match(text):
            # 在段落文本前插入分页标记
            # generator 会识别这个标记并插入分页符
            if not para.text.startswith('\x0C'):
                para.text = '\x0C' + para.text


def _detect_md_table_regions(paragraphs: list) -> list[dict]:
    """
    检测段落列表中的 markdown 表格区域。
    返回每个表格的 header cells、data rows 和段落索引。
    """
    regions = []
    i = 0
    while i < len(paragraphs):
        text = paragraphs[i].text.strip() if paragraphs[i].text else ''
        # 检测表格起始：以 | 开头和结尾的行
        if _MD_TABLE_RE.match(text) and not _MD_TABLE_SEP_RE.match(text):
            # 找到表格区域的起点
            all_indices = [i]
            header_cells = [c.strip() for c in text.strip('|').split('|')]

            j = i + 1
            # 检查下一行是否是分隔行 |----|----|
            if j < len(paragraphs):
                next_text = paragraphs[j].text.strip() if paragraphs[j].text else ''
                if _MD_TABLE_SEP_RE.match(next_text):
                    all_indices.append(j)
                    j += 1

            # 收集数据行
            data_rows = []
            while j < len(paragraphs):
                row_text = paragraphs[j].text.strip() if paragraphs[j].text else ''
                if _MD_TABLE_RE.match(row_text) and not _MD_TABLE_SEP_RE.match(row_text):
                    all_indices.append(j)
                    cells = [c.strip() for c in row_text.strip('|').split('|')]
                    data_rows.append(cells)
                    j += 1
                else:
                    break

            if header_cells:
                regions.append({
                    'header': header_cells,
                    'rows': data_rows,
                    'all_indices': all_indices,
                    'insert_after': i - 1,  # 在表格前一个段落之后插入
                })

            i = j
        else:
            i += 1

    return regions


def _apply_heading_format(para, text: str, font: str, size: int,
                           align: str, bold: bool) -> None:
    """给段落应用标题格式。"""
    para.text = text
    para.format.alignment = align
    para.format.first_line_indent_pt = 0
    if para.runs:
        para.runs[0].text = text
        for r in para.runs[1:]:
            r.text = ""
        for r in para.runs:
            r.format.font_name = font
            r.format.font_size_pt = float(size)
            r.format.bold = bold if bold else None


def set_paragraph_format_attr(model: DocumentModel, para_index: int,
                               attr: str, value: Any) -> None:
    """设置指定段落格式属性。"""
    if 0 <= para_index < len(model.paragraphs):
        para = model.paragraphs[para_index]
        if hasattr(para.format, attr):
            setattr(para.format, attr, value)


# ---------------------------------------------------------------------------
#  Batch apply: apply a list of modification dicts (AI / manual)
# ---------------------------------------------------------------------------

def apply_modifications(model: DocumentModel, modifications: list[dict]) -> DocumentModel:
    """
    批量应用修改列表。

    每个 modification dict 格式:
        type: "replace_text" | "set_format"
        location: "paragraph:N"
        value: new value
        attribute: (for set_format) 属性名
    """
    fixed = copy.deepcopy(model)

    for mod in modifications:
        mod_type = mod.get("type", "")
        location = mod.get("location", "")
        value = mod.get("value", "")
        para_idx = _extract_para_index(location)

        if para_idx is None:
            continue

        if mod_type == "replace_text":
            replace_paragraph_text(fixed, para_idx, value)
        elif mod_type == "set_format":
            attr = mod.get("attribute")
            if attr:
                set_paragraph_format_attr(fixed, para_idx, attr, value)

    logger.info(f"Applied {len(modifications)} custom modifications")
    return fixed


# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------

def _parse_mm_value(value: str | float | None) -> float | None:
    """Parse margin value like '3.7cm' or 37 to mm."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    value = str(value).strip()
    try:
        if "cm" in value:
            return float(value.replace("cm", "").strip()) * 10
        if "mm" in value:
            return float(value.replace("mm", "").strip())
        return float(value)
    except (ValueError, TypeError):
        logger.warning(f"无法解析 mm 值: {value!r}")
        return None


def _parse_pt_value(value: str | float | None) -> float | None:
    """Parse size/spacing value like '16pt' or 16 to pt."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace("pt", "").strip())
    except (ValueError, TypeError):
        logger.warning(f"无法解析 pt 值: {value!r}")
        return None


def _parse_indent_value(value: str | float | None) -> float | None:
    """Parse indent value like '2em' or '32pt' to pt."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    value = str(value).strip()
    try:
        if "em" in value:
            return float(value.replace("em", "").strip()) * 16
        return float(value.replace("pt", "").strip())
    except (ValueError, TypeError):
        logger.warning(f"无法解析 indent 值: {value!r}")
        return None


def _extract_para_index(location: str) -> int | None:
    """Extract paragraph index from 'paragraph:3'."""
    try:
        return int(location.split(":")[-1].split(",")[0])
    except (ValueError, IndexError):
        return None