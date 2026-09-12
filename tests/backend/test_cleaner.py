# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""格式清洗（clean_document）单元测试（原创实现）。"""

from core.document.models import DocumentModel, Paragraph, Run, RunFormat
from core.document.modifier import clean_document


def _para(text: str, runs: list[str] | None = None) -> Paragraph:
    r = runs or [text]
    return Paragraph(
        index=0,
        text=text,
        runs=[Run(index=i, text=t, format=RunFormat()) for i, t in enumerate(r)],
    )


def _model(texts: list[str], runs: list[list[str]] | None = None) -> DocumentModel:
    paras = []
    for i, t in enumerate(texts):
        r = runs[i] if runs else [t]
        p = _para(t, r)
        p.index = i
        paras.append(p)
    return DocumentModel(paragraphs=paras)


def test_collapse_ascii_spaces():
    m = _model(["这是   一段   正文"])
    report = clean_document(m)
    assert m.paragraphs[0].runs[0].text == "这是 一段 正文"
    assert report["spaces_collapsed"] == 2
    assert report["paragraphs_cleaned"] == 1


def test_collapse_fullwidth_spaces():
    m = _model(["正文\u3000\u3000\u3000内容"])
    clean_document(m)
    assert m.paragraphs[0].runs[0].text == "正文\u3000内容"


def test_strip_edges():
    m = _model(["  开头和结尾   "])
    clean_document(m)
    assert m.paragraphs[0].runs[0].text == "开头和结尾"
    assert m.paragraphs[0].text == "开头和结尾"


def test_text_synced_after_clean():
    m = _model(["a  b"], runs=[["a  ", "b"]])
    clean_document(m)
    # 连续空格压缩为 1 个；段内 run 边界空格保留（词间隔）
    assert m.paragraphs[0].text == "a b"


def test_blank_lines_merged():
    m = _model(["第一段", "", "", "第二段", "", "", "", "第三段"])
    report = clean_document(m)
    # 每组连续空行保留 1 个：2 空行组删 1、3 空行组删 2
    assert report["blank_lines_removed"] == 3
    texts = [p.text for p in m.paragraphs]
    assert texts == ["第一段", "", "第二段", "", "第三段"]


def test_clean_text_untouched():
    m = _model(["完全规范的正文内容", "2026年3月1日"])
    report = clean_document(m)
    assert report["paragraphs_cleaned"] == 0
    assert report["spaces_collapsed"] == 0
    assert report["edges_stripped"] == 0


def test_empty_model_safe():
    assert clean_document(DocumentModel())["paragraphs_cleaned"] == 0