"""
Rules API routes: manage check and fix rules across priority layers.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path

from config import RULES_DIR
from core.rules.manager import (
    list_rule_files,
    get_rule_content,
    save_rule,
    delete_rule,
    import_rule,
    export_rule,
    validate_rule,
    load_rules_merged,
)
from utils.logger import logger

router = APIRouter()


class RuleImportRequest(BaseModel):
    key: str
    yaml_text: str
    source_type: str = "user"


class RuleExportRequest(BaseModel):
    key: str
    source_type: str = "all"


class RuleUpdateRequest(BaseModel):
    content: dict
    source_type: str = "user"


@router.get("/")
async def list_rules(source: str = "all"):
    """List rules by source: all, official, custom, user."""
    rules = list_rule_files(source)
    logger.info(f"Listed {len(rules)} rules (source={source})")
    return {"rules": rules, "total": len(rules)}


@router.get("/{key}")
async def get_rule(key: str, source_type: str = "all"):
    """Get a single rule with full content."""
    rule = get_rule_content(key, source_type)
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule not found: {key}")
    return rule


@router.put("/{key}")
async def update_rule(key: str, body: RuleUpdateRequest):
    """Update or create a rule."""
    try:
        validate_rule(body.content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    ok = save_rule(key, body.content, body.source_type)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to save rule")
    return {"success": True, "key": key}


@router.delete("/{key}")
async def remove_rule(key: str, source_type: str = "user"):
    """Delete a user or custom rule."""
    ok = delete_rule(key, source_type)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Rule not found: {key}")
    return {"success": True, "key": key}


@router.post("/import")
async def import_rule_endpoint(body: RuleImportRequest):
    """Import a rule from YAML text."""
    result = import_rule(body.key, body.yaml_text, body.source_type)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Import failed"))
    return result


@router.post("/export")
async def export_rule_endpoint(body: RuleExportRequest):
    """Export a rule as YAML text."""
    yaml_str = export_rule(body.key, body.source_type)
    if yaml_str is None:
        raise HTTPException(status_code=404, detail=f"Rule not found: {body.key}")
    return {"key": body.key, "yaml_text": yaml_str}


@router.get("/merged/{doc_type}")
async def merged_rules(doc_type: str):
    """Get merged rules for a document type (priority: user > custom > official)."""
    merged = load_rules_merged(doc_type)
    return {
        "doc_type": doc_type,
        "rules": merged,
        "fix_rules_count": len(merged.get("fix_rules", [])),
        "check_rules_count": len(merged.get("check_rules", [])),
    }
