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
    if doc.optimized_path and Path(doc.optimized_path).exists():
        out_path = Path(doc.optimized_path)
    else:
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
