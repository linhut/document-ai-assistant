# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Rule engine: orchestrates loading, checking, and fixing using the rule system.
Supports priority layering: user > custom > official.
"""
from __future__ import annotations
from typing import Any
import copy

from core.document.models import DocumentModel
from core.rules.manager import load_rules_merged
from core.rules.checker import check_document, CheckIssue
from core.rules.fixer import apply_fixes
from utils.logger import logger


class RuleEngine:
    """
    Central rule engine that coordinates rule loading, checking, and fixing.
    """

    def __init__(self):
        self._rules_cache: dict[str, dict[str, Any]] = {}

    def load_rules(self, doc_type: str) -> dict[str, Any]:
        """
        Load rules for a document type (with priority: user > custom > official).
        """
        if doc_type not in self._rules_cache:
            self._rules_cache[doc_type] = load_rules_merged(doc_type)
            logger.info(f"Loaded and cached rules for type: {doc_type}")
        return self._rules_cache[doc_type]

    def check(self, model: DocumentModel, doc_type: str) -> list[CheckIssue]:
        rules = self.load_rules(doc_type)
        issues = check_document(model, rules)
        logger.info(f"Check complete: {len(issues)} issues found")
        return issues

    def fix(self, model: DocumentModel, doc_type: str, selected_rule_ids: list[str] | None = None) -> DocumentModel:
        rules = self.load_rules(doc_type)
        fixed_model = apply_fixes(model, rules, selected_rule_ids)
        logger.info(f"Fixes applied for type: {doc_type}")
        return fixed_model

    def check_and_fix(self, model: DocumentModel, doc_type: str, selected_rule_ids: list[str] | None = None) -> tuple[list[CheckIssue], DocumentModel]:
        rules = self.load_rules(doc_type)
        issues = check_document(model, rules)
        logger.info(f"Found {len(issues)} issues before fixing")
        fixed_model = apply_fixes(model, rules, selected_rule_ids)
        logger.info(f"Applied fixes for type: {doc_type}")
        return issues, fixed_model

    def clear_cache(self):
        self._rules_cache.clear()
        logger.info("Rules cache cleared")

    def available_types(self) -> list[str]:
        from core.rules.loader import list_available_types
        return list_available_types()
