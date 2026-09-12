# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""公文写作风格库（style_library）单元测试（原创实现）。"""

from ai.style_library import (
    DEAI_RULES,
    MODE_DESC,
    STYLE_PROFILES,
    build_rewrite_instruction,
    build_rewrite_prompt,
    get_profile,
    list_style_profiles,
)


def test_22_profiles_registered():
    assert len(STYLE_PROFILES) == 22


def test_every_profile_has_required_keys():
    for doc_type, profile in STYLE_PROFILES.items():
        assert doc_type, "profile key should be non-empty"
        assert profile["name"], f"{doc_type} missing name"
        assert isinstance(profile["structure"], list) and profile["structure"], f"{doc_type} structure"
        assert profile["tone"], f"{doc_type} missing tone"


def test_deai_rules_healthy():
    assert len(DEAI_RULES) >= 5
    assert len(set(DEAI_RULES)) == len(DEAI_RULES)  # 无重复


def test_instruction_contains_type_and_rules():
    instruction = build_rewrite_instruction("notice", "deai")
    assert "通知" in instruction
    assert "去 AI 味" in instruction
    assert "结构要点" in instruction


def test_fallback_to_generic_profile():
    assert get_profile("no_such_type")["name"] == "公文"


def test_prompt_contains_original_text():
    prompt = build_rewrite_prompt("这是待润色原文", "report", "polish")
    assert "这是待润色原文" in prompt
    assert "报告" in prompt


def test_all_modes_described():
    for mode, desc in MODE_DESC.items():
        instruction = build_rewrite_instruction("notice", mode)
        assert desc.split("：")[0] in instruction or "本次任务" in instruction


def test_list_profiles_shape():
    profiles = list_style_profiles()
    assert len(profiles) == 22
    assert {"document_type", "name"} <= set(profiles[0].keys())