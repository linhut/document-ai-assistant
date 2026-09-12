# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""文档要素语义校验单元测试（原创实现）。"""

from core.document.models import DocumentModel, Paragraph
from core.rules.semantic import semantic_check, SEMANTIC_RULES


def _model(texts: list[str]) -> DocumentModel:
    return DocumentModel(
        paragraphs=[Paragraph(index=i, text=t) for i, t in enumerate(texts)]
    )


def _ids(issues) -> set[str]:
    return {i.rule_id for i in issues}


def test_valid_document_has_no_semantic_issues():
    model = _model(
        [
            "××市人民政府关于印发《××方案》的通知",
            "各县（市、区）人民政府：",
            "现将《××方案》印发给你们，请认真贯彻执行。",
            "××市人民政府",
            "2026年3月1日",
        ]
    )
    assert semantic_check(model) == []


def test_doc_number_short_year_flagged():
    model = _model(["××发〔26〕1号", "正文内容", "××市人民政府", "2026年3月1日"])
    issues = semantic_check(model)
    assert "CHK-S001" in _ids(issues)
    assert any("4 位" in i.reason for i in issues)


def test_doc_number_wrong_bracket_flagged():
    model = _model(["××发[2026]1号", "正文内容", "××市人民政府", "2026年3月1日"])
    assert "CHK-S001" in _ids(semantic_check(model))


def test_doc_number_leading_zero_flagged():
    model = _model(["××发〔2026〕01号", "正文内容", "××市人民政府", "2026年3月1日"])
    assert "CHK-S001" in _ids(semantic_check(model))


def test_dash_date_flagged():
    model = _model(["正文内容", "××市人民政府", "2026-09-11"])
    issues = semantic_check(model)
    assert "CHK-S002" in _ids(issues)
    assert any("年月日" in i.reason for i in issues)


def test_invalid_date_range_flagged():
    model = _model(["正文内容", "××市人民政府", "2026年13月40日"])
    assert "CHK-S003" in _ids(semantic_check(model))


def test_missing_day_flagged():
    model = _model(["正文内容", "××市人民政府", "2026年9月"])
    assert "CHK-S002" in _ids(semantic_check(model))


def test_missing_signature_flagged():
    model = _model(
        [
            "这是一段非常长的正文内容，用来模拟缺少发文机关署名的情况，"
            "长度超过五十个字以确保不会被误判为署名段落，而是被判定为正文。",
            "2026年3月1日",
        ]
    )
    assert "CHK-S004" in _ids(semantic_check(model))


def test_empty_document_safe():
    assert semantic_check(DocumentModel()) == []


def test_semantic_rules_registry_consistent():
    assert {r["id"] for r in SEMANTIC_RULES} == {"CHK-S001", "CHK-S002", "CHK-S003", "CHK-S004"}