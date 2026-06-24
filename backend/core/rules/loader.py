"""
YAML rule file loader. Reads rule definitions from the rules/ directory.
"""
from pathlib import Path
from typing import Any
import yaml

from config import RULES_DIR
from utils.logger import logger


def load_rule_file(file_path: Path) -> dict[str, Any]:
    """Load a single YAML rule file and return its contents."""
    if not file_path.exists():
        logger.warning(f"Rule file not found: {file_path}")
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    logger.info(f"Loaded rule: {file_path.name}")
    return data or {}


def load_common_rules() -> dict[str, Any]:
    """Load the shared base rules (_common.yaml)."""
    return load_rule_file(RULES_DIR / "_common.yaml")


def load_rules_for_type(doc_type: str) -> dict[str, Any]:
    """
    Load type-specific rules merged on top of common rules.

    Args:
        doc_type: One of notice, request, report, letter, meeting,
                  decision, announcement, notice_public.

    Returns:
        Merged rule dictionary.
    """
    common = load_common_rules()
    type_file = RULES_DIR / f"{doc_type}.yaml"
    type_rules = load_rule_file(type_file)

    # Deep merge: type-specific overrides common
    merged = _deep_merge(common, type_rules)
    return merged


def list_available_types() -> list[str]:
    """Return a list of document type identifiers that have rule files."""
    types = []
    for f in RULES_DIR.glob("*.yaml"):
        if f.stem.startswith("_"):
            continue
        types.append(f.stem)
    return sorted(types)


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base (override wins)."""
    result = base.copy()
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = val
    return result
