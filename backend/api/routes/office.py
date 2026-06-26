# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Office Bridge API: Word/WPS 插件共用的 REST 接口。

所有 Office 插件通过此 API 与本地 Python Core Engine 通信。
插件端只需要做 HTTP 调用，不需要实现任何业务逻辑。
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import base64
import tempfile

from core.document.parser import parse_docx
from core.document.generator import generate_docx
from core.rules.engine import RuleEngine
from core.template.style_manager import list_templates, get_template
from core.template.generator import generate_docx_template, generate_dotx_template
from config import TEMP_DIR
from utils.logger import logger

router = APIRouter()
_rule_engine = RuleEngine()

# 临时文件目录
_BRIDGE_TMP = TEMP_DIR / "bridge"
_BRIDGE_TMP.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
#  Request / Response Models
# ---------------------------------------------------------------------------

class DocumentPayload(BaseModel):
    """文档传输格式：base64 编码的 docx 文件。"""
    document_base64: str
    document_type: str = "notice"
    filename: str = "document.docx"


class CheckResponse(BaseModel):
    total_issues: int
    p0_count: int
    p1_count: int
    p2_count: int
    issues: list[dict]


class FixResponse(BaseModel):
    fixes_applied: int
    document_base64: str
    message: str


class TemplateApplyRequest(BaseModel):
    template_id: str
    document_base64: str
    filename: str = "document.docx"


# ---------------------------------------------------------------------------
#  Health
# ---------------------------------------------------------------------------

@router.get("/health")
async def office_health():
    """Office 插件健康检查。"""
    return {
        "status": "ok",
        "service": "office-bridge",
        "version": "1.4.5",
        "capabilities": ["check", "fix", "ai-optimize", "templates", "apply-template"],
    }


# ---------------------------------------------------------------------------
#  Document Check
# ---------------------------------------------------------------------------

@router.post("/check", response_model=CheckResponse)
async def office_check(payload: DocumentPayload):
    """
    检查 Office 文档格式。

    接收 base64 编码的 docx，返回检查结果。
    """
    try:
        doc_path = _decode_to_temp(payload.document_base64, payload.filename)
        model = parse_docx(doc_path)
        issues = _rule_engine.check(model, payload.document_type)

        return CheckResponse(
            total_issues=len(issues),
            p0_count=sum(1 for i in issues if i.severity == "P0"),
            p1_count=sum(1 for i in issues if i.severity == "P1"),
            p2_count=sum(1 for i in issues if i.severity == "P2"),
            issues=[
                {
                    "severity": i.severity,
                    "rule_id": i.rule_id,
                    "name": i.name,
                    "location": i.location,
                    "original_text": i.original_text[:100],
                    "suggested_fix": i.suggested_fix,
                    "reason": i.reason,
                }
                for i in issues
            ],
        )
    except Exception as e:
        logger.error(f"Office check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
#  Document Fix
# ---------------------------------------------------------------------------

@router.post("/fix", response_model=FixResponse)
async def office_fix(payload: DocumentPayload):
    """
    一键格式规范。

    接收 base64 编码的 docx，返回修复后的 docx（base64）。
    """
    try:
        doc_path = _decode_to_temp(payload.document_base64, payload.filename)
        model = parse_docx(doc_path)
        issues, fixed_model = _rule_engine.check_and_fix(model, payload.document_type)

        # 生成修复后的文档
        out_path = _BRIDGE_TMP / f"fixed_{payload.filename}"
        generate_docx(fixed_model, out_path)

        # 编码为 base64
        with open(out_path, "rb") as f:
            fixed_b64 = base64.b64encode(f.read()).decode("utf-8")

        return FixResponse(
            fixes_applied=len(issues),
            document_base64=fixed_b64,
            message=f"已应用 {len(issues)} 项修复",
        )
    except Exception as e:
        logger.error(f"Office fix failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
#  AI Optimize
# ---------------------------------------------------------------------------

@router.post("/ai-optimize")
async def office_ai_optimize(payload: DocumentPayload):
    """
    AI 优化文档。

    暂时返回格式检查结果 + AI 分析提示。
    完整 AI 优化需要 Provider 配置。
    """
    try:
        doc_path = _decode_to_temp(payload.document_base64, payload.filename)
        model = parse_docx(doc_path)
        issues = _rule_engine.check(model, payload.document_type)

        return {
            "total_issues": len(issues),
            "message": f"发现 {len(issues)} 个格式问题，建议先使用'规范排版'修复格式",
            "ai_available": False,
            "note": "AI 优化功能需要在设置中配置 AI Provider",
        }
    except Exception as e:
        logger.error(f"Office AI optimize failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
#  Templates
# ---------------------------------------------------------------------------

@router.get("/templates")
async def office_list_templates(source: str = "all"):
    """获取样式模板列表。"""
    return {"templates": list_templates(source)}


@router.get("/templates/{template_id}")
async def office_get_template(template_id: str):
    """获取单个模板详情。"""
    template = get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template not found: {template_id}")
    return template


# ---------------------------------------------------------------------------
#  Apply Template / Generate Template
# ---------------------------------------------------------------------------

@router.post("/apply-template")
async def office_apply_template(payload: TemplateApplyRequest):
    """
    应用模板样式到文档。

    将模板的样式定义应用到现有文档的格式上。
    """
    try:
        doc_path = _decode_to_temp(payload.document_base64, payload.filename)
        model = parse_docx(doc_path)

        template = get_template(payload.template_id)
        if not template:
            raise HTTPException(status_code=404, detail=f"Template not found: {payload.template_id}")

        # 使用模板的 fix_rules 或直接应用样式
        from core.rules.manager import load_rules_merged
        rules = load_rules_merged(payload.template_id)
        _, fixed_model = _rule_engine.check_and_fix(model, payload.template_id)

        out_path = _BRIDGE_TMP / f"styled_{payload.filename}"
        generate_docx(fixed_model, out_path)

        with open(out_path, "rb") as f:
            styled_b64 = base64.b64encode(f.read()).decode("utf-8")

        return {
            "success": True,
            "document_base64": styled_b64,
            "template_applied": payload.template_id,
            "message": f"已应用 {template.get('name', payload.template_id)} 样式",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Apply template failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-template")
async def office_generate_template(template_id: str, format: str = "docx"):
    """
    生成模板文件下载。

    Args:
        template_id: 模板 ID
        format: 输出格式 "docx" | "dotx"
    """
    try:
        output_dir = _BRIDGE_TMP / "generated"
        output_dir.mkdir(parents=True, exist_ok=True)

        if format == "dotx":
            output_path = output_dir / f"{template_id}_template.dotx"
            generate_dotx_template(template_id, output_path)
        else:
            output_path = output_dir / f"{template_id}_template.docx"
            generate_docx_template(template_id, output_path)

        media_type = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.template"
            if format == "dotx"
            else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        return FileResponse(
            path=str(output_path),
            filename=output_path.name,
            media_type=media_type,
        )
    except Exception as e:
        logger.error(f"Generate template failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------

def _decode_to_temp(b64_data: str, filename: str) -> Path:
    """将 base64 数据解码为临时文件。"""
    data = base64.b64decode(b64_data)
    tmp_path = _BRIDGE_TMP / filename
    with open(tmp_path, "wb") as f:
        f.write(data)
    return tmp_path