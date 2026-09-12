# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""保持版式内容编辑（run 级 diff）单元测试（原创实现）。"""

from core.document.content_diff import (
    common_prefix_len,
    common_suffix_len,
    plan_run_updates,
)
from core.document.models import DocumentModel, Paragraph, Run, RunFormat
from core.document.modifier import apply_paragraph_edits


def _para(text: str, run_texts: list[str]) -> Paragraph:
    return Paragraph(
        index=0,
        text=text,
        runs=[Run(index=i, text=t, format=RunFormat()) for i, t in enumerate(run_texts)],
    )


def test_common_prefix_suffix():
    assert common_prefix_len("甲乙丙", "甲乙X丙") == 2
    assert common_suffix_len("甲乙丙", "甲乙X丙", 2) == 1


def test_plan_middle_insert_keeps_other_runs():
    p = _para("甲乙丙丁", ["甲", "乙丙", "丁"])
    plan = plan_run_updates(p, "甲乙X丁")
    # 变更落在 run1（起始偏移 1）：head 变为 "乙"+ "X"
    assert plan == {1: "乙X"}


def test_plan_suffix_add_keeps_prefix_run():
    p = _para("甲乙", ["甲", "乙"])
    plan = plan_run_updates(p, "甲乙丙")
    assert plan == {1: "乙丙"}


def test_plan_no_change_empty():
    p = _para("相同", ["相", "同"])
    assert plan_run_updates(p, "相同") == {}


def test_plan_no_runs_marks_minus_one():
    p = Paragraph(index=0, text="旧", runs=[])
    assert plan_run_updates(p, "新") == {-1: "新"}


def test_apply_edits_preserves_tuple_format():
    model = DocumentModel(
        paragraphs=[_para("甲乙丙丁", ["甲", "乙丙", "丁"])]
    )
    count = apply_paragraph_edits(model, {0: "甲乙X丁"})
    assert count == 1
    runs = model.paragraphs[0].runs
    assert [r.text for r in runs] == ["甲", "乙X", "丁"]
    assert model.paragraphs[0].text == "甲乙X丁"


def test_apply_edits_skips_bad_indices():
    model = DocumentModel(paragraphs=[_para("内容", ["内", "容"])])
    count = apply_paragraph_edits(model, {99: "越界", "str": "非整数", 0: "内容"})
    assert count == 0


def test_apply_edits_unchanged_text_not_counted():
    model = DocumentModel(paragraphs=[_para("不变", ["不", "变"])])
    assert apply_paragraph_edits(model, {0: "不变"}) == 0


def test_apply_edits_multiple_paragraphs():
    model = DocumentModel(
        paragraphs=[_para("段落一", ["段", "落", "一"]), _para("段落二", ["段", "落", "二"])]
    )
    count = apply_paragraph_edits(model, {0: "修改一", 1: "改二"})
    assert count == 2
    assert model.paragraphs[0].text == "修改一"
    assert model.paragraphs[1].text == "改二"