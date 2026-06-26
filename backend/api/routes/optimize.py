# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Optimize API routes: auto-fix and document generation.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path

from db.database import get_db
from api.schemas.api_models import OptimizeRequest, OptimizeResponse
from services import document_service as svc
from services.document_service import _OPTIMIZED_SUFFIX

router = APIRouter()


# ---------------------------------------------------------------------------
#  Markdown 格式转换（前端实时预览用）— 必须在 /{doc_id} 之前定义
# ---------------------------------------------------------------------------

from pydantic import BaseModel
from typing import Any


class ParagraphData(BaseModel):
    text: str
    role: str | None = None
    is_heading: bool = False
    heading_level: int | None = None
    format: dict[str, Any] = {}


class MarkdownConvertRequest(BaseModel):
    paragraphs: list[ParagraphData]


@router.post("/convert-markdown")
async def convert_markdown_text(body: MarkdownConvertRequest):
    """对段落文本执行 Markdown 格式识别与转换，返回转换后的段落。"""
    from core.document.models import (
        DocumentModel, DocumentMetadata, PageSetup,
        Paragraph, ParagraphFormat, Run, RunFormat,
    )
    from core.document.modifier import convert_markdown

    model = DocumentModel(
        metadata=DocumentMetadata(), page_setup=PageSetup(),
        paragraphs=[], tables=[], headers=[], footers=[],
    )

    for i, p in enumerate(body.paragraphs):
        rf = RunFormat(font_name=p.format.get('font_name'), font_size_pt=p.format.get('font_size_pt'), bold=p.format.get('bold'))
        pf = ParagraphFormat(alignment=p.format.get('alignment'), first_line_indent_pt=p.format.get('first_line_indent_pt'), line_spacing_pt=p.format.get('line_spacing_pt'))
        model.paragraphs.append(Paragraph(index=i, text=p.text, is_heading=p.is_heading, heading_level=p.heading_level, role=p.role, runs=[Run(index=0, text=p.text, format=rf)], format=pf))

    changes = convert_markdown(model)

    result = []
    for p in model.paragraphs:
        rf = p.runs[0].format if p.runs else RunFormat()
        result.append({
            "text": p.text, "role": p.role, "is_heading": p.is_heading, "heading_level": p.heading_level,
            "format": {"alignment": p.format.alignment, "first_line_indent_pt": p.format.first_line_indent_pt, "font_name": rf.font_name, "font_size_pt": rf.font_size_pt, "line_spacing_pt": p.format.line_spacing_pt, "bold": rf.bold},
        })

    return {"success": True, "changes": changes, "paragraphs": result}


# ---------------------------------------------------------------------------
#  文档优化
# ---------------------------------------------------------------------------


@router.post("/{doc_id}", response_model=OptimizeResponse)
async def run_optimize(doc_id: int, req: OptimizeRequest | None = None, db: Session = Depends(get_db)):
    """Run auto-optimization on a document."""
    doc_type = req.document_type if req else None
    apply_fixes = req.apply_fixes if req else True
    selected_rule_ids = req.selected_rule_ids if req else None
    try:
        result = svc.optimize_document(db, doc_id, doc_type, apply_fixes, selected_rule_ids)
    except ValueError as e:
        msg = str(e)
        # 区分"文档未找到"(404)和其他错误(422/500)
        if "not found" in msg.lower() or "未找到" in msg:
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=422, detail=msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return OptimizeResponse(
        document_id=result["document_id"],
        output_path=result["output_path"],
        fixes_applied=result["fixes_applied"],
        message=f"优化完成，已应用 {result['fixes_applied']} 项修复",
    )


@router.get("/{doc_id}/download")
async def download_optimized(doc_id: int, db: Session = Depends(get_db)):
    """Download the optimized document."""
    doc = svc.get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # 优先使用 DB 中存储的 optimized_path（由 optimize_document 写入）
    out_path = None
    if doc.optimized_path:
        p = Path(doc.optimized_path)
        if p.exists():
            out_path = p
        else:
            # 尝试按文件名在 OUTPUT_DIR 中查找
            from config import OUTPUT_DIR
            fallback = OUTPUT_DIR / p.name
            if fallback.exists():
                out_path = fallback
    if not out_path:
        # 回退：按命名规则拼接路径
        out_name = Path(doc.filename).stem + _OPTIMIZED_SUFFIX
        from config import OUTPUT_DIR
        out_path = OUTPUT_DIR / out_name
        if not out_path.exists():
            raise HTTPException(status_code=404, detail="Optimized file not found. Run optimize first.")

    return FileResponse(
        path=str(out_path),
        filename=out_path.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
