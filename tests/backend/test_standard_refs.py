# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""GB/T 9704 标准条款映射（证据链）单元测试。"""

from core.rules.standard_refs import resolve_standard_ref, standard_ref_note


def test_title_font_maps_to_title_clause():
    assert resolve_standard_ref({"field": "title.font"}) == "7.2.4"


def test_body_font_maps_to_body_clause():
    assert resolve_standard_ref({"field": "body.font"}) == "7.3.3"


def test_page_margins_maps_to_page_clause():
    assert resolve_standard_ref({"field": "page_setup.margins.top"}) == "6.1"


def test_heading_levels_map_to_font_clause():
    assert resolve_standard_ref({"field": "heading_1.font"}) == "6.2"
    assert resolve_standard_ref({"field": "heading_2.size"}) == "6.2"
    assert resolve_standard_ref({"field": "heading_3.first_line_indent"}) == "6.2"


def test_explicit_standard_ref_overrides_field_map():
    rule = {"field": "title.font", "standard_ref": "6.2"}
    assert resolve_standard_ref(rule) == "6.2"


def test_unknown_field_returns_empty():
    assert resolve_standard_ref({"field": "unknown.xyz"}) == ""


def test_note_returned_for_known_field():
    note = standard_ref_note("date.align")
    assert "成文日期" in note


def test_rule_without_field_returns_empty():
    assert resolve_standard_ref({"id": "FIX-C001"}) == ""