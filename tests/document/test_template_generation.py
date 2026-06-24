"""
模板生成测试：验证所有公文类型的模板均可正常生成，且字体 XML 正确。
"""
import sys
import os
from pathlib import Path
import zipfile
from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "backend"))

from core.rules.loader import load_rules_for_type
from core.document.generator import generate_docx
from core.document.models import DocumentModel, Paragraph, Run, RunFormat, ParagraphFormat, PageSetup

TEMPLATE_TYPES = [
    "notice", "request", "report", "letter", "meeting",
    "decision", "announcement", "notice_public",
]

OUTPUT_DIR = Path(__file__).resolve().parent / "output" / "templates"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
REQUIRED_EAST_ASIA = {"方正小标宋简体", "仿宋_GB2312"}


def _parse_margin(value):
    if isinstance(value, (int, float)):
        return float(value)
    v = str(value).strip()
    if "cm" in v:
        return float(v.replace("cm", "").strip()) * 10
    if "mm" in v:
        return float(v.replace("mm", "").strip())
    return float(v)


def _parse_size(value):
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value).replace("pt", "").strip())


def _create_test_model(doc_type, rules):
    """Create a minimal DocumentModel with title + body for testing."""
    tc = rules.get("title", {})
    bc = rules.get("body", {})
    psr = rules.get("page_setup", {})
    m = psr.get("margins", {})

    doc = DocumentModel(
        filename=f"{doc_type}_template.docx",
        page_setup=PageSetup(
            paper_width_mm=210, paper_height_mm=297,
            margin_top_mm=_parse_margin(m.get("top", "3.7cm")),
            margin_bottom_mm=_parse_margin(m.get("bottom", "3.5cm")),
            margin_left_mm=_parse_margin(m.get("left", "2.8cm")),
            margin_right_mm=_parse_margin(m.get("right", "2.6cm")),
        ),
    )

    title_para = Paragraph(
        text=f"关于XXX事项的{doc_type}",
        index=0, is_heading=True, heading_level=1,
        format=ParagraphFormat(alignment="center"),
        runs=[Run(index=0, text=f"关于XXX事项的{doc_type}",
            format=RunFormat(
                font_name=tc.get("font", "方正小标宋简体"),
                font_size_pt=_parse_size(tc.get("size", 22)),
            ))]
    )
    doc.paragraphs.append(title_para)

    body_para = Paragraph(
        text="正文内容测试ABC123，包含中文字符和英文数字。",
        index=1,
        format=ParagraphFormat(alignment="justify", first_line_indent_pt=32, line_spacing_pt=28.95),
        runs=[Run(index=0, text="正文内容测试ABC123，包含中文字符和英文数字。",
            format=RunFormat(
                font_name=bc.get("font", "仿宋_GB2312"),
                font_size_pt=_parse_size(bc.get("size", 16)),
            ))]
    )
    doc.paragraphs.append(body_para)

    return doc


def test_template_generation():
    """测试：所有公文类型模板可正常生成 docx 文件。"""
    print("=" * 60)
    print("TEST 1: Template Generation")
    print("=" * 60)

    for t in TEMPLATE_TYPES:
        rules = load_rules_for_type(t)
        model = _create_test_model(t, rules)
        output_path = OUTPUT_DIR / f"{t}_template_test.docx"
        result = generate_docx(model, output_path)
        assert result.exists(), f"模板生成失败: {t}"
        assert result.stat().st_size > 2000, f"模板文件过小: {t} -> {result.stat().st_size} bytes"
        print(f"  PASS: {t} -> {result.stat().st_size} bytes")

    print("  ALL PASSED\n")


def test_font_xml_east_asia():
    """测试：docx 内部 XML 中 eastAsia 字体正确设置。"""
    print("=" * 60)
    print("TEST 2: Font XML - eastAsia Verification")
    print("=" * 60)

    for t in TEMPLATE_TYPES:
        fpath = OUTPUT_DIR / f"{t}_template_test.docx"
        with zipfile.ZipFile(fpath, 'r') as z:
            with z.open('word/document.xml') as xf:
                tree = etree.parse(xf)

        root = tree.getroot()
        rfonts = root.findall('.//w:rFonts', NS)

        east_asias = set()
        ms_found = False

        for rf in rfonts:
            for attr_name, attr_value in rf.attrib.items():
                if 'MS' in str(attr_value):
                    ms_found = True
            ea = rf.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia')
            if ea:
                east_asias.add(ea)

        assert not ms_found, f"{t}: 发现 MS 替代字体!"
        assert REQUIRED_EAST_ASIA.issubset(east_asias), \
            f"{t}: eastAsia 不全, 实际={east_asias}, 期望包含={REQUIRED_EAST_ASIA}"
        print(f"  PASS: {t} eastAsia={sorted(east_asias)}, MS=False")

    print("  ALL PASSED\n")


def test_document_defaults():
    """测试：styles.xml 中 docDefaults 设置了正确的默认字体。"""
    print("=" * 60)
    print("TEST 3: Document Default Fonts (styles.xml)")
    print("=" * 60)

    fpath = OUTPUT_DIR / "notice_template_test.docx"
    with zipfile.ZipFile(fpath, 'r') as z:
        with z.open('word/styles.xml') as xf:
            tree = etree.parse(xf)

    root = tree.getroot()
    doc_defaults = root.find('.//w:docDefaults', NS)
    assert doc_defaults is not None, "docDefaults 未设置!"

    rFonts = doc_defaults.find('.//w:rPrDefault/w:rPr/w:rFonts', NS)
    assert rFonts is not None, "docDefaults 中无 rFonts 元素!"

    east_asia = rFonts.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia')
    ascii_font = rFonts.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii')

    assert east_asia == "仿宋_GB2312", f"docDefaults eastAsia 错误: {east_asia}"
    assert ascii_font == "Times New Roman", f"docDefaults ascii 错误: {ascii_font}"
    print(f"  PASS: docDefaults eastAsia={east_asia}, ascii={ascii_font}")
    print("  ALL PASSED\n")


def test_line_spacing():
    """测试：行距设置为固定值（EXACTLY）。"""
    print("=" * 60)
    print("TEST 4: Line Spacing Rule (EXACTLY)")
    print("=" * 60)

    fpath = OUTPUT_DIR / "notice_template_test.docx"
    with zipfile.ZipFile(fpath, 'r') as z:
        with z.open('word/document.xml') as xf:
            tree = etree.parse(xf)

    root = tree.getroot()
    spacings = root.findall('.//w:spacing', NS)

    for sp in spacings:
        line_rule = sp.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}lineRule')
        line_val = sp.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}line')
        if line_val:
            # lineRule should be "exact" for fixed line spacing
            if line_rule:
                assert line_rule == "exact", f"行距不是固定值: lineRule={line_rule}"
            print(f"  PASS: lineRule={line_rule or 'default'}, line={line_val}")

    print("  ALL PASSED\n")


def test_format_check_flow():
    """测试：格式检查流程完整性（parse -> check -> fix -> 验证）。"""
    print("=" * 60)
    print("TEST 5: Format Check + Fix Flow")
    print("=" * 60)

    from core.document.parser import parse_docx
    from core.document.generator import generate_docx
    from core.rules.engine import RuleEngine

    engine = RuleEngine()
    fix_output_dir = OUTPUT_DIR / "optimized"
    fix_output_dir.mkdir(parents=True, exist_ok=True)

    for t in ["notice", "report"]:
        fpath = OUTPUT_DIR / f"{t}_template_test.docx"
        model = parse_docx(str(fpath))

        # Step 1: Check - should find issues
        issues, fixed_model = engine.check_and_fix(model, t)
        assert len(issues) > 0, f"{t}: 格式检查未发现任何问题（预期应有检查结果）"

        # Step 2: Fix and generate optimized
        opt_path = fix_output_dir / f"{t}_optimized_test.docx"
        generate_docx(fixed_model, opt_path)

        # Step 3: Re-check optimized doc
        opt_model = parse_docx(str(opt_path))
        issues_after = engine.check(opt_model, t)
        p0_after = [i for i in issues_after if i.severity == "P0"]

        print(f"  {t}: before={len(issues)} issues -> after_fix={len(issues_after)} issues (P0={len(p0_after)})")

    print("  ALL PASSED\n")


if __name__ == "__main__":
    test_template_generation()
    test_font_xml_east_asia()
    test_document_defaults()
    test_line_spacing()
    test_format_check_flow()
    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)
