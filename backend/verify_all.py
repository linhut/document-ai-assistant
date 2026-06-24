"""
一键验证脚本 — 测试文档生成 + 字体 + 后端API
用法：cd backend && python verify_all.py
"""
import sys
import os
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

# 确保可以 import backend 模块
sys.path.insert(0, str(Path(__file__).parent))

WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def check(ok, msg):
    status = "✅" if ok else "❌"
    print(f"  {status} {msg}")
    return ok


def test_font_generation():
    """测试文档生成并验证字体 XML。"""
    section("1. 文档生成 + 字体验证")

    from core.document.models import DocumentModel, Paragraph, Run, RunFormat, ParagraphFormat, PageSetup
    from core.document.generator import generate_docx
    from core.document.font_utils import TITLE_FONT, BODY_FONT, LATIN_FONT

    model = DocumentModel(
        filename="verify_test.docx",
        page_setup=PageSetup(
            paper_width_mm=210, paper_height_mm=297,
            margin_top_mm=37, margin_bottom_mm=35,
            margin_left_mm=28, margin_right_mm=26,
        ),
        paragraphs=[
            Paragraph(
                text="关于XXX工作的通知", index=0, is_heading=True, heading_level=1,
                format=ParagraphFormat(alignment="center"),
                runs=[Run(index=0, text="关于XXX工作的通知", format=RunFormat(
                    font_name=TITLE_FONT, font_size_pt=22,
                ))],
            ),
            Paragraph(
                text="各部门、各单位：根据上级要求，现将有关事项通知如下。", index=1,
                format=ParagraphFormat(alignment="justify", first_line_indent_pt=32, line_spacing_pt=28.95),
                runs=[Run(index=0, text="各部门、各单位：根据上级要求，现将有关事项通知如下。", format=RunFormat(
                    font_name=BODY_FONT, font_size_pt=16,
                ))],
            ),
            # 无 run 的段落（测试默认字体回退）
            Paragraph(
                text="", index=2,
                format=ParagraphFormat(),
                runs=[],
            ),
        ],
    )

    output = Path(__file__).parent / "data" / "verify_test.docx"
    output.parent.mkdir(parents=True, exist_ok=True)
    generate_docx(model, output)

    check(output.exists(), f"文件生成成功: {output}")
    check(output.stat().st_size > 1000, f"文件大小: {output.stat().st_size} bytes")

    # 验证 XML
    with zipfile.ZipFile(output, "r") as zf:
        xml_content = zf.read("word/document.xml").decode("utf-8")

    root = ET.fromstring(xml_content)
    fonts_found = []
    for elem in root.iter():
        if elem.tag.endswith("}rFonts"):
            ea = elem.get(f"{{{WORD_NS}}}eastAsia")
            ascii_f = elem.get(f"{{{WORD_NS}}}ascii")
            hAnsi = elem.get(f"{{{WORD_NS}}}hAnsi")
            cs = elem.get(f"{{{WORD_NS}}}cs")
            fonts_found.append({"eastAsia": ea, "ascii": ascii_f, "hAnsi": hAnsi, "cs": cs})

    check(len(fonts_found) > 0, f"找到 {len(fonts_found)} 个字体设置")

    for i, f in enumerate(fonts_found):
        ea = f["eastAsia"]
        has_ea = ea is not None and ea != ""
        check(has_ea, f"  Run[{i}] eastAsia = {ea}")
        if ea and "MS " in ea:
            check(False, f"  Run[{i}] 发现无效字体: {ea}")

    # 检查 MS Gothic
    has_ms = "MS Gothic" in xml_content or "MS Mincho" in xml_content
    check(not has_ms, "document.xml 中无 MS Gothic/Mincho")

    # 检查 docDefaults
    try:
        with zipfile.ZipFile(output, "r") as zf:
            styles_xml = zf.read("word/styles.xml").decode("utf-8")
        has_defaults = "docDefaults" in styles_xml
        check(has_defaults, "styles.xml 包含 docDefaults")
    except:
        check(False, "styles.xml 读取失败")

    # --- 全面格式验证 ---
    section("1b. 页面设置 + 段落格式验证")
    from docx import Document as DocxDocument
    doc = DocxDocument(str(output))
    sec = doc.sections[0]

    # 页边距
    top_mm = round(sec.top_margin.mm, 1) if sec.top_margin else 0
    bottom_mm = round(sec.bottom_margin.mm, 1) if sec.bottom_margin else 0
    left_mm = round(sec.left_margin.mm, 1) if sec.left_margin else 0
    right_mm = round(sec.right_margin.mm, 1) if sec.right_margin else 0

    check(abs(top_mm - 37) < 3, f"上边距: {top_mm}mm (期望 37mm)")
    check(abs(bottom_mm - 35) < 3, f"下边距: {bottom_mm}mm (期望 35mm)")
    check(abs(left_mm - 28) < 3, f"左边距: {left_mm}mm (期望 28mm)")
    check(abs(right_mm - 26) < 3, f"右边距: {right_mm}mm (期望 26mm)")

    # 纸张
    w_mm = round(sec.page_width.mm, 1) if sec.page_width else 0
    h_mm = round(sec.page_height.mm, 1) if sec.page_height else 0
    check(abs(w_mm - 210) < 5, f"纸张宽度: {w_mm}mm (期望 210mm A4)")
    check(abs(h_mm - 297) < 5, f"纸张高度: {h_mm}mm (期望 297mm A4)")

    # 段落格式
    for i, para in enumerate(doc.paragraphs):
        if not para.text.strip():
            continue
        if i == 0:  # 标题
            align = para.alignment
            check(align is not None, f"标题对齐: {align}")
        if i == 1:  # 正文
            pfmt = para.paragraph_format
            indent = pfmt.first_line_indent
            if indent:
                indent_pt = round(indent.pt, 1)
                check(abs(indent_pt - 32) < 5, f"正文首行缩进: {indent_pt}pt (期望 32pt)")

    return output


def test_template_download():
    """测试模板下载功能。"""
    section("2. 模板生成测试")

    from core.rules.loader import load_rules_for_type
    from api.routes.template_download import _create_template_document
    from core.document.generator import generate_docx

    types = ["notice", "request", "report", "letter", "meeting", "decision", "announcement", "notice_public"]
    output_dir = Path(__file__).parent / "data" / "verify_templates"
    output_dir.mkdir(parents=True, exist_ok=True)

    all_ok = True
    for dtype in types:
        try:
            rules = load_rules_for_type(dtype)
            model = _create_template_document(dtype, rules)
            output = output_dir / f"{dtype}_template.docx"
            generate_docx(model, output)
            ok = output.exists() and output.stat().st_size > 1000
            check(ok, f"{dtype}: {output.stat().st_size if output.exists() else 0} bytes")
            if not ok:
                all_ok = False
        except Exception as e:
            check(False, f"{dtype}: {e}")
            all_ok = False

    return all_ok


def test_api_endpoints():
    """测试后端 API 是否可用。"""
    section("3. 后端 API 测试")
    import httpx
    import asyncio

    async def run():
        base = "http://127.0.0.1:8765"
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Health
            try:
                r = await client.get(f"{base}/api/health")
                check(r.status_code == 200, f"健康检查: {r.json()}")
            except Exception as e:
                check(False, f"后端未启动: {e}")
                return False

            # Fonts
            try:
                r = await client.get(f"{base}/api/settings/fonts")
                data = r.json()
                check(r.status_code == 200, f"字体列表: {data.get('total', 0)} 个字体")
            except Exception as e:
                check(False, f"字体API: {e}")

            # AI providers
            try:
                r = await client.get(f"{base}/api/ai/providers")
                data = r.json()
                providers = [p["name"] if isinstance(p, dict) else p for p in data.get("providers", [])]
                check(r.status_code == 200, f"AI Provider: {providers}")
            except Exception as e:
                check(False, f"AI API: {e}")

            return True

    return asyncio.run(run())


if __name__ == "__main__":
    section("AI 公文智能优化助手 — 一键验证")
    print(f"  Python: {sys.version}")
    print(f"  工作目录: {Path(__file__).parent}")

    doc_path = test_font_generation()
    test_template_download()
    test_api_endpoints()

    section("验证完成")
    print(f"\n  生成的测试文档: {doc_path}")
    print(f"  请用 Word 打开此文件验证字体是否正确。")
    print(f"  如果字体显示为「仿宋_GB2312」而非「MS Gothic」，则修复成功。\n")
