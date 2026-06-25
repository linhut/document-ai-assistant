# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Document modifier: applies a list of AI-provided or rule-based
modifications to the DocumentModel.
"""
from __future__ import annotations
import copy
from typing import Any

from core.document.models import DocumentModel
from utils.logger import logger


def apply_modifications(
    model: DocumentModel,
    modifications: list[dict[str, Any]],
) -> DocumentModel:
    """
    Apply a list of modification dicts to the document model.

    Each modification dict should have:
        - type: "replace_text" | "set_format"
        - location: "paragraph:N" or "paragraph:N,run:M"
        - before: original text (for verification)
        - after: replacement text

    Returns a new model with modifications applied.
    """
    fixed = copy.deepcopy(model)

    for mod in modifications:
        mod_type = mod.get("type", "")
        location = mod.get("location", "")
        after = mod.get("after", "")

        if mod_type == "replace_text":
            _apply_text_replace(fixed, location, after)
        elif mod_type == "set_format":
            _apply_format_change(fixed, location, mod)
        else:
            logger.warning(f"Unknown modification type: {mod_type}")

    logger.info(f"Applied {len(modifications)} modifications")
    return fixed


def _apply_text_replace(model: DocumentModel, location: str, new_text: str):
    """Replace text at the specified location."""
    para_idx = _extract_para_index(location)
    if para_idx is None or para_idx >= len(model.paragraphs):
        return
    para = model.paragraphs[para_idx]
    para.text = new_text
    # Update first run text if it exists
    if para.runs:
        para.runs[0].text = new_text
        for r in para.runs[1:]:
            r.text = ""


def _apply_format_change(model: DocumentModel, location: str, mod: dict):
    """Apply a format change at the specified location."""
    para_idx = _extract_para_index(location)
    if para_idx is None or para_idx >= len(model.paragraphs):
        return
    para = model.paragraphs[para_idx]

    attr = mod.get("attribute")
    value = mod.get("value")
    if attr and value is not None:
        if hasattr(para.format, attr):
            setattr(para.format, attr, value)


def _extract_para_index(location: str) -> int | None:
    """Extract paragraph index from a location string like 'paragraph:3'."""
    try:
        parts = location.replace("paragraph:", "").split(",")
        return int(parts[0])
    except (ValueError, IndexError):
        return None
