"""
Rule Manager 测试：三层规则合并、CRUD、导入导出、验证
"""
import pytest
import yaml
import tempfile
import shutil
from pathlib import Path

from core.rules.manager import (
    load_rules_merged, list_rule_files, get_rule_content,
    save_rule, delete_rule, import_rule, export_rule, validate_rule,
    OFFICIAL_RULES_DIR, CUSTOM_RULES_DIR, USER_RULES_DIR,
)


# ===========================================================================
#  Test 1: 三层规则合并
# ===========================================================================

class TestRuleMerge:
    """测试三层规则合并逻辑。"""

    def test_load_merged_has_common_base(self):
        """合并后的规则包含 _common.yaml 的基础配置。"""
        merged = load_rules_merged("notice")
        assert "page_setup" in merged, "缺少 page_setup（来自 _common.yaml）"
        assert "body" in merged, "缺少 body 配置"

    def test_load_merged_has_type_rules(self):
        """合并后的规则包含类型专属规则。"""
        merged = load_rules_merged("notice")
        assert "title" in merged, "通知规则缺少 title 配置"
        assert "check_rules" in merged, "通知规则缺少 check_rules"
        assert "fix_rules" in merged, "通知规则缺少 fix_rules"

    def test_load_merged_has_check_and_fix_rules(self):
        """合并后的规则同时有 check_rules 和 fix_rules 列表。"""
        for doc_type in ["notice", "request", "report", "letter",
                          "meeting", "decision", "announcement", "notice_public"]:
            merged = load_rules_merged(doc_type)
            assert isinstance(merged.get("check_rules", []), list), \
                f"{doc_type}: check_rules 应为列表"
            assert isinstance(merged.get("fix_rules", []), list), \
                f"{doc_type}: fix_rules 应为列表"
            assert len(merged.get("check_rules", [])) > 0, \
                f"{doc_type}: check_rules 为空"
            assert len(merged.get("fix_rules", [])) > 0, \
                f"{doc_type}: fix_rules 为空"

    def test_user_rule_overrides_official(self, tmp_path):
        """用户规则应覆盖官方规则中的同名字段。"""
        # 创建临时用户规则文件
        user_dir = tmp_path / "user_rules"
        user_dir.mkdir()
        user_rule = {
            "body": {
                "font": "测试字体",
                "size": "18pt",
            }
        }
        with open(user_dir / "notice.yaml", "w", encoding="utf-8") as f:
            yaml.dump(user_rule, f, allow_unicode=True)

        # 临时替换 USER_RULES_DIR
        import core.rules.manager as mgr
        orig_dir = mgr.USER_RULES_DIR
        mgr.USER_RULES_DIR = user_dir
        try:
            merged = load_rules_merged("notice")
            assert merged["body"]["font"] == "测试字体", \
                "用户规则未能覆盖官方规则的 body.font"
            assert merged["body"]["size"] == "18pt", \
                "用户规则未能覆盖官方规则的 body.size"
            # 保留官方规则中的其他字段
            assert "line_spacing" in merged["body"], \
                "用户规则覆盖时丢失了官方规则的其他字段"
        finally:
            mgr.USER_RULES_DIR = orig_dir


# ===========================================================================
#  Test 2: CRUD 操作
# ===========================================================================

class TestRuleCRUD:
    """测试规则的创建、读取、更新、删除。"""

    def test_save_and_get_user_rule(self, tmp_path):
        """保存并读取用户规则。"""
        import core.rules.manager as mgr
        orig_dir = mgr.USER_RULES_DIR
        mgr.USER_RULES_DIR = tmp_path / "user"
        mgr.USER_RULES_DIR.mkdir(parents=True, exist_ok=True)
        try:
            content = {
                "template_name": "测试规则",
                "body": {"font": "SimSun", "size": "14pt"},
                "check_rules": [
                    {"id": "CHK-TEST-001", "name": "测试检查", "severity": "P1", "field": "body.font"}
                ],
            }
            ok = save_rule("test_rule", content, "user")
            assert ok, "保存规则失败"

            result = get_rule_content("test_rule", "user")
            assert result is not None, "读取规则失败"
            assert result["content"]["template_name"] == "测试规则"
        finally:
            mgr.USER_RULES_DIR = orig_dir

    def test_delete_user_rule(self, tmp_path):
        """删除用户规则。"""
        import core.rules.manager as mgr
        orig_dir = mgr.USER_RULES_DIR
        mgr.USER_RULES_DIR = tmp_path / "user"
        mgr.USER_RULES_DIR.mkdir(parents=True, exist_ok=True)
        try:
            save_rule("to_delete", {"template_name": "删除测试"}, "user")
            ok = delete_rule("to_delete", "user")
            assert ok, "删除规则失败"
            assert get_rule_content("to_delete", "user") is None, "规则未被真正删除"
        finally:
            mgr.USER_RULES_DIR = orig_dir

    def test_cannot_delete_official_rule(self):
        """不能删除官方规则。"""
        ok = delete_rule("notice", "official")
        assert ok is False, "不应该允许删除官方规则"

    def test_list_rules_returns_all_sources(self):
        """列出所有来源的规则。"""
        rules = list_rule_files("all")
        assert len(rules) > 0, "没有找到任何规则"
        sources = {r["source_type"] for r in rules}
        assert "official" in sources, "缺少 official 规则"

    def test_list_rules_filter_by_source(self):
        """按来源筛选规则。"""
        official = list_rule_files("official")
        assert all(r["source_type"] == "official" for r in official), \
            "筛选 official 时返回了其他来源的规则"


# ===========================================================================
#  Test 3: 导入/导出
# ===========================================================================

class TestRuleImportExport:
    """测试规则导入导出。"""

    def test_import_valid_yaml(self, tmp_path):
        """导入合法的 YAML 规则。"""
        import core.rules.manager as mgr
        orig_dir = mgr.USER_RULES_DIR
        mgr.USER_RULES_DIR = tmp_path / "user"
        mgr.USER_RULES_DIR.mkdir(parents=True, exist_ok=True)
        try:
            yaml_text = yaml.dump({
                "template_name": "导入测试",
                "body": {"font": "仿宋_GB2312"},
                "check_rules": [
                    {"id": "CHK-IMP-001", "name": "导入检查", "severity": "P0", "field": "body.font"}
                ],
            }, allow_unicode=True)
            result = import_rule("imported_rule", yaml_text, "user")
            assert result["success"], f"导入失败: {result.get('error')}"
        finally:
            mgr.USER_RULES_DIR = orig_dir

    def test_import_invalid_yaml(self):
        """导入非法 YAML 应返回失败。"""
        result = import_rule("bad_rule", "{{{{invalid yaml}}}}", "user")
        assert result["success"] is False

    def test_export_existing_rule(self):
        """导出已存在的官方规则。"""
        yaml_str = export_rule("notice", "official")
        assert yaml_str is not None, "导出通知规则失败"
        data = yaml.safe_load(yaml_str)
        assert isinstance(data, dict)
        assert "template_name" in data or "check_rules" in data


# ===========================================================================
#  Test 4: 验证
# ===========================================================================

class TestRuleValidation:
    """测试规则验证逻辑。"""

    def test_validate_valid_rule(self):
        """合法规则通过验证。"""
        rule = {
            "body": {"font": "仿宋_GB2312"},
            "check_rules": [
                {"id": "CHK-001", "name": "测试", "severity": "P0", "field": "body.font"}
            ],
            "fix_rules": [
                {"id": "FIX-001", "action": "set_font", "target": "body", "value": "仿宋_GB2312"}
            ],
        }
        validate_rule(rule)  # Should not raise

    def test_validate_rejects_non_dict(self):
        """非字典类型应抛出 ValueError。"""
        with pytest.raises(ValueError):
            validate_rule("not a dict")

    def test_validate_rejects_empty_rule(self):
        """空规则应抛出 ValueError。"""
        with pytest.raises(ValueError):
            validate_rule({})

    def test_validate_rejects_bad_fix_rule(self):
        """缺少 action 的 fix_rule 应抛出 ValueError。"""
        with pytest.raises(ValueError):
            validate_rule({
                "fix_rules": [{"id": "FIX-001", "target": "body"}]
            })

    def test_validate_rejects_bad_check_rule(self):
        """缺少 id 的 check_rule 应抛出 ValueError。"""
        with pytest.raises(ValueError):
            validate_rule({
                "check_rules": [{"name": "test", "severity": "P0"}]
            })


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])