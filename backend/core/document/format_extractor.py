# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Format Extractor: 从已排版的 DocumentModel 中自动提取格式信息，
生成完整的 YAML 规则模板（check_rules + fix_rules）。
"""
from __future__ import annotations
from collections import Counter
from typing import Any

from core.document.models import DocumentModel, Paragraph
from utils.logger import logger


def _most_common(values: list) -> Any:
    """取众数，忽略 None 值。"""
    valid = [v for v in values if v is not None]
    if not valid:
        return None
    return Counter(valid).most_common(1)[0][0]


def _round_pt(val: float | None, decimals: int = 2) -> str | None:
    """将 pt 值格式化为字符串，如 '16pt', '28.95pt'。"""
    if val is None:
        return None
    rounded = round(val, decimals)
    if rounded == int(rounded):
        return f"{int(rounded)}pt"
    return f"{rounded}pt"


def _pt_to_indent_str(val: float | None) -> str | None:
    """首行缩进: 如果是 16pt 的整数倍，转为 'Nem' 格式。"""
    if val is None:
        return None
    em_count = round(val / 16)
    if em_count >= 1 and abs(val - em_count * 16) < 2:
        return f"{em_count}em"
    return _round_pt(val)


def _mm_to_cm(val: float | None) -> str | None:
    """mm 转 cm 字符串，如 '3.7cm'。"""
    if val is None:
        return None
    cm = round(val / 10, 1)
    return f"{cm}cm"


class FormatExtractor:
    """
    从 DocumentModel 提取各类段落的代表格式，
    生成完整的规则 YAML 结构。
    """

    def __init__(self, model: DocumentModel):
        self.model = model
        self._group_paragraphs()

    def _group_paragraphs(self) -> None:
        """按 heading_level 和 role 分组段落。"""
        self.title_paras: list[Paragraph] = []
        self.h1_paras: list[Paragraph] = []
        self.h2_paras: list[Paragraph] = []
        self.h3_paras: list[Paragraph] = []
        self.body_paras: list[Paragraph] = []
        self.signature_paras: list[Paragraph] = []
        self.date_paras: list[Paragraph] = []

        for p in self.model.paragraphs:
            if not p.text.strip():
                continue

            if p.heading_level == 0 or p.role == 'title':
                self.title_paras.append(p)
            elif p.heading_level == 1:
                self.h1_paras.append(p)
            elif p.heading_level == 2:
                self.h2_paras.append(p)
            elif p.heading_level == 3:
                self.h3_paras.append(p)
            elif p.role == 'signature':
                self.signature_paras.append(p)
            elif p.role == 'date':
                self.date_paras.append(p)
            elif p.role in ('body', 'recipient', 'attachment', 'cc', 'notes', None):
                self.body_paras.append(p)

    def _extract_run_format(self, paras: list[Paragraph]) -> dict:
        """从一组段落中提取 run 级别的众数格式。"""
        fonts = []
        sizes = []
        bolds = []
        for p in paras:
            for r in p.runs:
                if r.format.font_name:
                    fonts.append(r.format.font_name)
                if r.format.font_size_pt:
                    sizes.append(r.format.font_size_pt)
                if r.format.bold is not None:
                    bolds.append(r.format.bold)
        return {
            'font': _most_common(fonts),
            'size': _most_common(sizes),
            'bold': _most_common(bolds),
        }

    def _extract_para_format(self, paras: list[Paragraph]) -> dict:
        """从一组段落中提取段落级别的众数格式。"""
        alignments = []
        indents = []
        line_spacings = []
        for p in paras:
            if p.format.alignment:
                alignments.append(p.format.alignment)
            if p.format.first_line_indent_pt is not None:
                indents.append(p.format.first_line_indent_pt)
            if p.format.line_spacing_pt is not None:
                line_spacings.append(p.format.line_spacing_pt)
        return {
            'alignment': _most_common(alignments),
            'first_line_indent_pt': _most_common(indents),
            'line_spacing_pt': _most_common(line_spacings),
        }

    def extract_all(self) -> dict[str, Any]:
        """
        提取全部格式信息，返回完整结构。

        Returns:
            {
                'template_name': str,
                'sections': { title, heading_1, heading_2, heading_3, body, signature, date },
                'page_setup': { margins, paper },
                'summary': { 各区段的格式摘要 },
            }
        """
        sections = {}
        summary = {}

        # 提取各段落类别
        categories = [
            ('title', self.title_paras, '公文标题'),
            ('heading_1', self.h1_paras, '一级标题'),
            ('heading_2', self.h2_paras, '二级标题'),
            ('heading_3', self.h3_paras, '三级标题'),
            ('body', self.body_paras, '正文'),
            ('signature', self.signature_paras, '落款'),
            ('date', self.date_paras, '日期'),
        ]

        for key, paras, label in categories:
            if not paras:
                sections[key] = None
                continue

            rf = self._extract_run_format(paras)
            pf = self._extract_para_format(paras)

            section = {}
            if rf['font']:
                section['font'] = rf['font']
            if rf['size'] is not None:
                section['size'] = _round_pt(rf['size'])
            if rf['bold'] is not None and rf['bold']:
                section['bold'] = True
            if pf['alignment']:
                section['align'] = pf['alignment']
            if pf['first_line_indent_pt'] is not None:
                section['first_line_indent'] = _pt_to_indent_str(pf['first_line_indent_pt'])
            if pf['line_spacing_pt'] is not None:
                section['line_spacing'] = _round_pt(pf['line_spacing_pt'])

            sections[key] = section

            # 构建摘要
            parts = []
            if rf['font']:
                parts.append(rf['font'])
            if rf['size']:
                parts.append(_round_pt(rf['size']))
            if pf['alignment']:
                parts.append(pf['alignment'])
            if pf['first_line_indent_pt']:
                parts.append(f"缩进{_pt_to_indent_str(pf['first_line_indent_pt'])}")
            if pf['line_spacing_pt']:
                parts.append(f"行距{_round_pt(pf['line_spacing_pt'])}")
            if rf['bold']:
                parts.append('加粗')
            summary[key] = {'label': label, 'count': len(paras), 'format': ', '.join(parts) if parts else '未检测到'}

        # 页面设置
        ps = self.model.page_setup
        page_setup = {
            'margin_top': _mm_to_cm(ps.margin_top_mm),
            'margin_bottom': _mm_to_cm(ps.margin_bottom_mm),
            'margin_left': _mm_to_cm(ps.margin_left_mm),
            'margin_right': _mm_to_cm(ps.margin_right_mm),
            'paper_width_mm': ps.paper_width_mm,
            'paper_height_mm': ps.paper_height_mm,
        }
        summary['page_setup'] = {
            'label': '页面设置',
            'count': 1,
            'format': f"上{page_setup['margin_top']} 下{page_setup['margin_bottom']} "
                      f"左{page_setup['margin_left']} 右{page_setup['margin_right']}"
        }

        return {
            'sections': sections,
            'page_setup': page_setup,
            'summary': summary,
        }

    def generate_yaml(self, template_name: str, document_type: str) -> dict:
        """
        生成完整的规则 YAML 结构。

        Returns:
            可直接 yaml.dump 的 dict
        """
        extracted = self.extract_all()
        sections = extracted['sections']
        ps = extracted['page_setup']

        # 构建格式定义区
        yaml_data: dict[str, Any] = {
            'template_name': template_name,
            'document_type': document_type,
        }

        # 页面设置
        yaml_data['page_setup'] = {
            'paper_size': 'A4',
            'paper_width_mm': ps.get('paper_width_mm', 210),
            'paper_height_mm': ps.get('paper_height_mm', 297),
            'margins': {
                'top': ps.get('margin_top', '3.7cm'),
                'bottom': ps.get('margin_bottom', '3.5cm'),
                'left': ps.get('margin_left', '2.8cm'),
                'right': ps.get('margin_right', '2.6cm'),
            }
        }

        # 各段落格式
        section_key_map = {
            'title': 'doc_title',
            'heading_1': 'heading_1',
            'heading_2': 'heading_2',
            'heading_3': 'heading_3',
            'body': 'body',
            'signature': 'signature',
            'date': 'date',
        }
        for src_key, dst_key in section_key_map.items():
            sec = sections.get(src_key)
            if sec:
                yaml_data[dst_key] = sec

        # 生成 check_rules 和 fix_rules
        check_rules, fix_rules = self._generate_rules(sections, ps)
        yaml_data['check_rules'] = check_rules
        yaml_data['fix_rules'] = fix_rules

        return yaml_data

    def _generate_rules(self, sections: dict, ps: dict) -> tuple[list, list]:
        """根据提取的格式生成 check_rules 和 fix_rules。"""
        check_rules = []
        fix_rules = []
        chk_idx = 0
        fix_idx = 0

        def _add_check(field: str, expected: Any, name: str, message: str, severity: str = 'P0') -> str:
            nonlocal chk_idx
            chk_idx += 1
            rule_id = f"CHK-U{chk_idx:03d}"
            check_rules.append({
                'id': rule_id,
                'name': name,
                'severity': severity,
                'field': field,
                'expected': expected,
                'message': message,
            })
            return rule_id

        def _add_fix(ref_check: str, action: str, target: str, value: Any) -> None:
            nonlocal fix_idx
            fix_idx += 1
            fix_rules.append({
                'id': f"FIX-U{fix_idx:03d}",
                'ref_check': ref_check,
                'action': action,
                'target': target,
                'value': value,
            })

        # 标题规则
        title = sections.get('title')
        if title:
            if title.get('font'):
                ref = _add_check('title.font', title['font'],
                                 '标题字体检查', f'标题应使用{title["font"]}')
                _add_fix(ref, 'set_font', 'doc_title', title['font'])
            if title.get('size'):
                ref = _add_check('title.size', title['size'],
                                 '标题字号检查', f'标题应使用{title["size"]}')
                _add_fix(ref, 'set_size', 'doc_title', title['size'])
            if title.get('align'):
                ref = _add_check('title.align', title['align'],
                                 '标题对齐检查', f'标题应{self._align_label(title["align"])}')
                _add_fix(ref, 'set_alignment', 'doc_title', title['align'])

        # 一级标题
        h1 = sections.get('heading_1')
        if h1:
            if h1.get('font'):
                ref = _add_check('heading_1.font', h1['font'],
                                 '一级标题字体检查', f'一级标题应使用{h1["font"]}')
                _add_fix(ref, 'set_font', 'heading_1', h1['font'])
            if h1.get('size'):
                ref = _add_check('heading_1.size', h1['size'],
                                 '一级标题字号检查', f'一级标题应使用{h1["size"]}')
                _add_fix(ref, 'set_size', 'heading_1', h1['size'])

        # 二级标题
        h2 = sections.get('heading_2')
        if h2:
            if h2.get('font'):
                ref = _add_check('heading_2.font', h2['font'],
                                 '二级标题字体检查', f'二级标题应使用{h2["font"]}')
                _add_fix(ref, 'set_font', 'heading_2', h2['font'])
            if h2.get('size'):
                ref = _add_check('heading_2.size', h2['size'],
                                 '二级标题字号检查', f'二级标题应使用{h2["size"]}')
                _add_fix(ref, 'set_size', 'heading_2', h2['size'])

        # 三级标题
        h3 = sections.get('heading_3')
        if h3:
            if h3.get('font'):
                ref = _add_check('heading_3.font', h3['font'],
                                 '三级标题字体检查', f'三级标题应使用{h3["font"]}')
                _add_fix(ref, 'set_font', 'heading_3', h3['font'])
            if h3.get('bold'):
                _add_fix(None, 'set_bold', 'heading_3', True)

        # 正文规则
        body = sections.get('body')
        if body:
            if body.get('font'):
                ref = _add_check('body.font', body['font'],
                                 '正文字体检查', f'正文应使用{body["font"]}')
                _add_fix(ref, 'set_font', 'body', body['font'])
            if body.get('size'):
                ref = _add_check('body.size', body['size'],
                                 '正文字号检查', f'正文应使用{body["size"]}')
                _add_fix(ref, 'set_size', 'body', body['size'])
            if body.get('line_spacing'):
                ref = _add_check('body.line_spacing', body['line_spacing'],
                                 '正文行距检查', f'正文行距应为{body["line_spacing"]}', 'P1')
                _add_fix(ref, 'set_line_spacing', 'body', body['line_spacing'])
            if body.get('first_line_indent'):
                ref = _add_check('body.first_line_indent', body['first_line_indent'],
                                 '正文首行缩进检查', f'正文首行应缩进{body["first_line_indent"]}', 'P1')
                _add_fix(ref, 'set_first_line_indent', 'body', body['first_line_indent'])
            if body.get('align'):
                ref = _add_check('body.align', body['align'],
                                 '正文对齐检查', f'正文应{self._align_label(body["align"])}', 'P1')
                _add_fix(ref, 'set_alignment', 'body', body['align'])

        # 页面边距
        margin_map = {
            'margin_top': ('上边距', 'top'),
            'margin_bottom': ('下边距', 'bottom'),
            'margin_left': ('左边距', 'left'),
            'margin_right': ('右边距', 'right'),
        }
        for key, (label, margin_key) in margin_map.items():
            val = ps.get(key)
            if val:
                ref = _add_check(f'page_setup.margins.{margin_key}', val,
                                 f'{label}检查', f'{label}应为{val}（GB/T 9704标准）')
                _add_fix(ref, 'set_page_margins', 'page_setup', {margin_key: val})

        # 落款
        sig = sections.get('signature')
        if sig and sig.get('align'):
            ref = _add_check('signature.align', sig['align'],
                             '落款对齐检查', f'落款应{self._align_label(sig["align"])}', 'P1')
            _add_fix(ref, 'set_alignment', 'signature', sig['align'])

        return check_rules, fix_rules

    @staticmethod
    def _align_label(align: str) -> str:
        """对齐方式的人类可读标签。"""
        return {
            'left': '左对齐',
            'center': '居中',
            'right': '右对齐',
            'justify': '两端对齐',
        }.get(align, align)


def extract_format_from_docx(file_path: str) -> dict:
    """
    便捷入口：解析 docx 并提取格式信息。

    Args:
        file_path: .docx 文件路径

    Returns:
        {
            'sections': ...,
            'page_setup': ...,
            'summary': ...,
        }
    """
    from core.document.parser import parse_docx
    model = parse_docx(file_path)
    extractor = FormatExtractor(model)
    return extractor.extract_all()


def generate_template_from_docx(file_path: str, template_name: str, document_type: str) -> dict:
    """
    便捷入口：从 docx 生成完整的规则 YAML 结构。

    Args:
        file_path: .docx 文件路径
        template_name: 模板名称
        document_type: 文档类型标识

    Returns:
        可直接 yaml.dump 的 dict
    """
    from core.document.parser import parse_docx
    model = parse_docx(file_path)
    extractor = FormatExtractor(model)
    return extractor.generate_yaml(template_name, document_type)
