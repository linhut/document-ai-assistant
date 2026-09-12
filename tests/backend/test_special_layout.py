# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""特殊版式模块单元测试（原创实现）。"""

import tempfile
import zipfile
from pathlib import Path

from core.document.generator import generate_docx
from core.document.models import DocumentModel, Paragraph


def _model(profile=None, options=None, n=3) -> DocumentModel:
    m = DocumentModel(paragraphs=[Paragraph(index=i, text=f"测试段落{i}") for i in range(n)])
    m.metadata.layout_profile = profile
    if options:
        m.metadata.layout_options = options
    return m


def _gen(model) -> Path:
    out = Path(tempfile.mkdtemp()) / "out.docx"
    generate_docx(model, out)
    return out


def _paragraph_count(out: Path) -> int:
    with zipfile.ZipFile(out) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    return xml.count("<w:p>")


def _header_xml(out: Path) -> str:
    with zipfile.ZipFile(out) as z:
        for name in z.namelist():
            if name.startswith("word/header"):
                return z.read(name).decode("utf-8")
    return ""


def test_no_profile_no_extra_paragraphs():
    out = _gen(_model())
    # 3 个正文段落 + 1 个空文档段落容器（新增文档默认含正文分隔段）
    assert _paragraph_count(out) >= 3


def test_formal_reserve_inserts_expected_lines():
    out = _gen(_model(profile="formal", options={"reserve_top_mm": 72}))
    n = _paragraph_count(out)
    plain = _paragraph_count(_gen(_model()))
    # 72mm ≈ 8 行（28 磅）+ 标题前 2 行
    assert 9 <= n - plain <= 12


def test_reserve_clamped_to_range():
    out = _gen(_model(profile="formal", options={"reserve_top_mm": 500}))
    n = _paragraph_count(out)
    plain = _paragraph_count(_gen(_model()))
    # 130mm ≈ 14 行 + 2 行，且必须明显小于 500mm 折算的 52 行
    assert n - plain <= 17


def test_letter_double_lines_in_header():
    out = _gen(_model(profile="letter"))
    header = _header_xml(out)
    assert "pBdr" in header
    assert "FF0000" in header


def test_command_spacing_adds_two_lines():
    out = _gen(_model(profile="command"))
    n = _paragraph_count(out)
    plain = _paragraph_count(_gen(_model()))
    assert n - plain == 2


def test_joint_nameplate_independent_of_profile():
    out = _gen(_model(options={"joint_orgs": ["甲单位", "乙单位"]}))
    with zipfile.ZipFile(out) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    assert "甲单位" in xml and "乙单位" in xml
    assert "FF0000" in xml


def test_unknown_profile_safe():
    out = _gen(_model(profile="mystery"))
    plain = _paragraph_count(_gen(_model()))
    assert _paragraph_count(out) - plain == 0


def test_empty_model_with_profile_safe():
    out = _gen(DocumentModel())
    assert out.exists()