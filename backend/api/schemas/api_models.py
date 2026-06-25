# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Pydantic models for API request/response schemas.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


# --- Document ---
class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    document_type: Optional[str] = None
    status: str = "uploaded"
    page_count: int = 0
    paragraph_count: int = 0
    created_at: Optional[datetime] = None


class DocumentInfo(BaseModel):
    id: int
    filename: str
    file_path: str
    file_hash: str
    document_type: Optional[str] = None
    status: str
    page_count: int = 0
    paragraph_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# --- Check ---
class CheckIssueResponse(BaseModel):
    id: int
    check_type: str
    severity: str
    rule_id: Optional[str] = None
    location: Optional[str] = None
    original_text: Optional[str] = None
    suggested_fix: Optional[str] = None
    reason: Optional[str] = None
    status: str = "pending"


class CheckResultResponse(BaseModel):
    document_id: int
    total_issues: int
    p0_count: int = 0
    p1_count: int = 0
    p2_count: int = 0
    issues: list[CheckIssueResponse] = []


class CheckRequest(BaseModel):
    document_type: Optional[str] = None


class IssueActionRequest(BaseModel):
    action: str  # accept / dismiss


# --- Optimize ---
class OptimizeRequest(BaseModel):
    document_type: Optional[str] = None
    apply_fixes: bool = True
    apply_ai_suggestions: bool = False
    selected_rule_ids: Optional[list[str]] = Field(default=None, description="仅应用指定规则ID的修复，为None时应用全部")


class OptimizeResponse(BaseModel):
    document_id: int
    output_path: str
    fixes_applied: int = 0
    message: str = ""


# --- AI ---
class AIAnalyzeRequest(BaseModel):
    document_id: int


class AIProofreadRequest(BaseModel):
    text: str


class AIRewriteRequest(BaseModel):
    text: str
    context: str = ""


class AIConfigRequest(BaseModel):
    provider: str
    api_key: str
    base_url: str = ""
    model: str = ""
    extra_params: Optional[str] = None


class AIConfigResponse(BaseModel):
    id: int
    provider: str
    base_url: Optional[str] = None
    model: Optional[str] = None
    is_active: bool = False
    has_api_key: bool = False


class AITestResponse(BaseModel):
    success: bool
    message: str = ""


class AISuggestion(BaseModel):
    """单条 AI 建议，用于应用到文档。"""
    original: str = Field(description="原文片段")
    suggestion: str = Field(description="建议修改后的内容")


class ApplyAIRequest(BaseModel):
    """AI 建议应用请求。"""
    suggestions: list[AISuggestion] = Field(description="要应用的 AI 建议列表")


# --- Settings ---
class RuleTypeResponse(BaseModel):
    types: list[str] = []
