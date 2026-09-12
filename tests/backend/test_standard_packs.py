# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""标准包机制单元测试（原创实现）。"""

from core.rules import packs as packs_mod
from core.rules.manager import load_rules_merged
from core.rules.packs import get_active_pack, list_standard_packs, set_active_pack


def test_enterprise_pack_listed():
    assert "enterprise" in list_standard_packs()


def test_load_rules_with_pack_overrides_official():
    rules = load_rules_merged("notice", pack="enterprise")
    # 格式段覆盖：正文字号 16pt -> 14pt
    assert rules["body"]["size"] == "14pt"
    # 同 field 检查规则按优先级覆盖：标题字体期望变为黑体
    title_rules = [r for r in rules["check_rules"] if r.get("field") == "title.font"]
    assert title_rules, "pack 应与官方规则合并出标题字体检查"
    assert title_rules[0]["expected"] == "黑体"


def test_load_rules_without_pack_is_official(tmp_path, monkeypatch):
    monkeypatch.setattr(packs_mod, "ACTIVE_PACK_FILE", tmp_path / "active_pack.json")
    rules = load_rules_merged("notice")
    assert rules["body"]["size"] == "16pt"
    title_rules = [r for r in rules["check_rules"] if r.get("field") == "title.font"]
    assert title_rules[0]["expected"] == "方正小标宋简体"


def test_set_get_active_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(packs_mod, "ACTIVE_PACK_FILE", tmp_path / "active_pack.json")
    assert set_active_pack("enterprise") is True
    assert get_active_pack() == "enterprise"
    assert set_active_pack(None) is True
    assert get_active_pack() is None


def test_invalid_pack_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(packs_mod, "ACTIVE_PACK_FILE", tmp_path / "active_pack.json")
    assert set_active_pack("no_such_pack") is False
    assert get_active_pack() is None