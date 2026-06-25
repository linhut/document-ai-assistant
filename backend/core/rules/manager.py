# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
﻿"""
Rule Manager: unified rule loading with priority layering.

Priority: user > custom > official
"""
from __future__ import annotations
import copy
import json
import yaml
from pathlib import Path
from typing import Any

from config import RULES_DIR, CUSTOM_RULES_DIR, USER_RULES_DIR
from utils.logger import logger

# Rule source directories
OFFICIAL_RULES_DIR = RULES_DIR  # rules/official（只读，捆绑在安装目录）


def _ensure_dirs() -> None:
    CUSTOM_RULES_DIR.mkdir(parents=True, exist_ok=True)
    USER_RULES_DIR.mkdir(parents=True, exist_ok=True)


def list_rule_files(source: str = "all") -> list[dict]:
    """List rule files from given source: official, custom, user, all."""
    _ensure_dirs()
    result = []
    dirs = {
        "official": OFFICIAL_RULES_DIR,
        "custom": CUSTOM_RULES_DIR,
        "user": USER_RULES_DIR,
    }
    for source_type, d in dirs.items():
        if source != "all" and source != source_type:
            continue
        for f in sorted(d.glob("*.yaml")):
            if f.stem.startswith("_"):
                continue
            result.append({
                "key": f.stem,
                "name": f.stem,
                "source_type": source_type,
                "path": str(f),
                "size": f.stat().st_size,
                "enabled": True,
            })
    return result


def load_rules_merged(doc_type: str = "") -> dict[str, Any]:
    """
    Load and merge rules for a document type with priority:
    official < custom < user
    """
    _ensure_dirs()
    merged: dict[str, Any] = {}

    layers = [
        ("official", OFFICIAL_RULES_DIR),
        ("custom", CUSTOM_RULES_DIR),
        ("user", USER_RULES_DIR),
    ]
    for _source, dir_path in layers:
        # Load common
        common_file = dir_path / "_common.yaml"
        if common_file.exists():
            _deep_merge(merged, _load_yaml(common_file))

        # Load type-specific
        if doc_type:
            type_file = dir_path / f"{doc_type}.yaml"
            if type_file.exists():
                _deep_merge(merged, _load_yaml(type_file))

    # Merge fix_rules and check_rules as distinct lists, not overwritten
    merged.setdefault("fix_rules", [])
    merged.setdefault("check_rules", [])
    return merged


def _load_yaml(path: Path) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception as exc:
        logger.error(f"Failed to load rule {path}: {exc}")
        return {}


def _deep_merge(base: dict, overlay: dict) -> None:
    """Merge overlay into base in-place, with list concatenation for fix_rules/check_rules."""
    for key, val in overlay.items():
        if key in ("fix_rules", "check_rules") and isinstance(val, list):
            base.setdefault(key, []).extend(val)
        elif key in base and isinstance(base[key], dict) and isinstance(val, dict):
            _deep_merge(base[key], val)
        else:
            base[key] = copy.deepcopy(val)


def save_rule(key: str, content: dict, source_type: str = "user") -> bool:
    """Save a user/custom rule YAML file."""
    _ensure_dirs()
    if source_type == "custom":
        dir_path = CUSTOM_RULES_DIR
    else:
        dir_path = USER_RULES_DIR
    file_path = dir_path / f"{key}.yaml"
    try:
        with open(file_path, "w", encoding="utf-8") as fh:
            yaml.dump(content, fh, allow_unicode=True, default_flow_style=False)
        logger.info(f"Rule saved: {file_path}")
        return True
    except Exception as exc:
        logger.error(f"Failed to save rule {file_path}: {exc}")
        return False


def delete_rule(key: str, source_type: str = "user") -> bool:
    """Delete a user/custom rule YAML file."""
    _ensure_dirs()
    if source_type == "custom":
        dir_path = CUSTOM_RULES_DIR
    else:
        dir_path = USER_RULES_DIR
    file_path = dir_path / f"{key}.yaml"
    try:
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Rule deleted: {file_path}")
            return True
        return False
    except Exception as exc:
        logger.error(f"Failed to delete rule {file_path}: {exc}")
        return False


def get_rule_content(key: str, source_type: str = "all") -> dict | None:
    """Get full content of a rule by key."""
    _ensure_dirs()
    dirs = {
        "official": OFFICIAL_RULES_DIR,
        "custom": CUSTOM_RULES_DIR,
        "user": USER_RULES_DIR,
    }
    for st, d in dirs.items():
        if source_type != "all" and source_type != st:
            continue
        f = d / f"{key}.yaml"
        if f.exists():
            return {
                "key": key,
                "source_type": st,
                "content": _load_yaml(f),
                "path": str(f),
            }
    return None


def export_rule(key: str, source_type: str = "all") -> str | None:
    """Export a rule as YAML string."""
    rule = get_rule_content(key, source_type)
    if not rule:
        return None
    return yaml.dump(rule["content"], allow_unicode=True, default_flow_style=False)


def import_rule(key: str, yaml_text: str, source_type: str = "user") -> dict:
    """Import a rule from YAML text."""
    try:
        content = yaml.safe_load(yaml_text)
        if not isinstance(content, dict):
            raise ValueError("Invalid YAML: not a dict")
        # Validate basic structure
        validate_rule(content)
        ok = save_rule(key, content, source_type)
        return {"success": ok, "key": key, "source_type": source_type}
    except Exception as exc:
        logger.error(f"Failed to import rule {key}: {exc}")
        return {"success": False, "error": str(exc)}


def validate_rule(rule: dict) -> None:
    """
    Validate rule structure.
    Raises ValueError on failure.
    """
    if not isinstance(rule, dict):
        raise ValueError("Rule must be a dictionary")

    # Must have at least some meaningful content
    has_format = any(k in rule for k in ("title", "body", "page_setup"))
    has_rules = any(k in rule for k in ("check_rules", "fix_rules"))
    if not has_format and not has_rules:
        raise ValueError(
            "Rule must have at least one of: title, body, page_setup, check_rules, fix_rules"
        )

    # Validate check_rules structure
    for cr in rule.get("check_rules", []):
        if not isinstance(cr, dict):
            raise ValueError("Each check_rule must be a dict")
        if "id" not in cr:
            raise ValueError("Each check_rule must have an 'id'")
        if "severity" not in cr:
            raise ValueError(f"check_rule '{cr.get('id', '?')}' must have 'severity'")

    # Validate fix_rules structure
    for fr in rule.get("fix_rules", []):
        if not isinstance(fr, dict):
            raise ValueError("Each fix_rule must be a dict")
        if "action" not in fr:
            raise ValueError(f"Each fix_rule must have an 'action', got: {fr}")

    # Validate check_rules and fix_rules are lists if present
    for field in ("fix_rules", "check_rules"):
        if field in rule and not isinstance(rule[field], list):
            raise ValueError(f"'{field}' must be a list")


def override_priority(source_type: str) -> int:
    """Return override priority: higher value = higher priority."""
    return {"official": 0, "custom": 1, "user": 2}.get(source_type, -1)
