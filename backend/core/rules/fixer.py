"""
Rule-based fixer: interprets YAML fix_rules and delegates to DocumentModifier.

职责：只负责解析 YAML 规则，翻译为 modifier 的函数调用。
不直接修改 DocumentModel 的任何属性。

流程：
  YAML fix_rules → apply_fixes() → modifier.*() → DocumentModel
"""
from __future__ import annotations
from typing import Any

from core.document.models import DocumentModel
from core.document.modifier import (
    modify_font, modify_size, modify_alignment, modify_line_spacing,
    modify_first_line_indent, modify_margins,
    remove_extra_spaces, remove_extra_blank_lines,
    _parse_pt_value, _parse_indent_value,
)
from utils.logger import logger


# Map YAML action names to modifier functions
_ACTION_MAP = {
    "set_font": lambda model, target, value, _rules: modify_font(model, target, value),
    "set_size": lambda model, target, value, _rules: modify_size(model, target, _parse_pt_value(value)),
    "set_alignment": lambda model, target, value, _rules: modify_alignment(model, target, str(value)),
    "set_align": lambda model, target, value, _rules: modify_alignment(model, target, str(value)),
    "set_line_spacing": lambda model, target, value, _rules: modify_line_spacing(model, target, _parse_pt_value(value)),
    "set_first_line_indent": lambda model, target, value, _rules: modify_first_line_indent(model, target, _parse_indent_value(value)),
    "set_indent": lambda model, target, value, _rules: modify_first_line_indent(model, target, _parse_indent_value(value)),
    "set_margins": lambda model, target, value, _rules: modify_margins(model, value),
    "set_page_margins": lambda model, target, value, _rules: modify_margins(model, value),
    "remove_extra_spaces": lambda model, _target, _value, _rules: remove_extra_spaces(model),
    "remove_extra_blank_lines": lambda model, _target, _value, _rules: remove_extra_blank_lines(model),
}


def apply_fixes(model: DocumentModel, rules: dict[str, Any], selected_rule_ids: list[str] | None = None) -> DocumentModel:
    """
    Apply fix_rules from the rule set to the document model.

    This is the entry point called by RuleEngine.check_and_fix().
    It interprets each YAML fix rule and delegates to DocumentModifier.

    Args:
        model: The document model to fix (will be deep-copied)
        rules: Merged rule dictionary (common + type-specific)
        selected_rule_ids: If provided, only apply rules with these IDs.
                          If None, apply all rules.

    Returns:
        A new DocumentModel with fixes applied
    """
    import copy
    fixed = copy.deepcopy(model)
    fix_rules = rules.get("fix_rules", [])

    # 如果指定了规则ID列表，只应用匹配的规则
    if selected_rule_ids is not None:
        selected_set = set(selected_rule_ids)
        fix_rules = [r for r in fix_rules if r.get("id") in selected_set]
        logger.info(f"Applying {len(fix_rules)} of {len(rules.get('fix_rules', []))} fix rules (selected: {len(selected_set)} IDs)")
    else:
        logger.info(f"Applying {len(fix_rules)} fix rules")

    for rule in fix_rules:
        action = rule.get("action", "")
        target = rule.get("target", "")
        value = rule.get("value")

        handler = _ACTION_MAP.get(action)
        if handler:
            # 需要 value 的动作（排除 remove_* 类动作）
            if value is None and action not in ("remove_extra_spaces", "remove_extra_blank_lines"):
                logger.warning(f"Fix rule {rule.get('id', '?')} missing required 'value' field, skipping")
                continue
            handler(fixed, target, value, rules)
        else:
            logger.warning(f"Unknown fix action: {action}")

    logger.info("Fixes applied successfully")
    return fixed