# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Document CRUD API routes.
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path

from db.database import get_db
from api.schemas.api_models import DocumentUploadResponse, DocumentInfo
from services import document_service as svc
from config import TEMP_DIR
from utils.logger import logger

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a .docx file."""
    if not file.filename or not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are supported")

    # Check file size (max 10MB recommended, warn if larger)
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)

    if file_size_mb > 50:
        raise HTTPException(
            status_code=400,
            detail="文件过大（超过 50MB）。建议使用 WPS/Word 插件处理大型文档。"
        )

    if file_size_mb > 10:
        logger.warning(f"Large file detected: {file.filename} ({file_size_mb:.2f} MB)")

    # Save to temp location; service will copy to UPLOAD_DIR
    # 安全处理文件名（防止路径遍历攻击）
    import re
    safe_name = re.sub(r'[^\w一-鿿._-]', '_', file.filename or "upload.docx")
    tmp_dir = TEMP_DIR
    tmp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = tmp_dir / safe_name

    with open(temp_path, "wb") as f:
        f.write(content)

    try:
        doc = svc.upload_document(db, temp_path, file.filename)
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return DocumentUploadResponse(
        id=doc.id,
        filename=doc.filename,
        file_path=doc.file_path,
        document_type=doc.document_type,
        status=doc.status,
        page_count=doc.page_count,
        paragraph_count=doc.paragraph_count,
        created_at=doc.created_at,
    )


@router.get("/{doc_id}", response_model=DocumentInfo)
async def get_document(doc_id: int, db: Session = Depends(get_db)):
    """Get document info by ID."""
    doc = svc.get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentInfo(
        id=doc.id,
        filename=doc.filename,
        file_path=doc.file_path,
        file_hash=doc.file_hash,
        document_type=doc.document_type,
        status=doc.status,
        page_count=doc.page_count,
        paragraph_count=doc.paragraph_count,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.get("/")
async def list_documents(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all documents."""
    docs = svc.list_documents(db, skip, limit)
    return [
        DocumentInfo(
            id=d.id, filename=d.filename, file_path=d.file_path,
            file_hash=d.file_hash, document_type=d.document_type,
            status=d.status, page_count=d.page_count,
            paragraph_count=d.paragraph_count,
            created_at=d.created_at, updated_at=d.updated_at,
        )
        for d in docs
    ]


@router.post("/{doc_id}/validate")
async def validate_document(doc_id: int, db: Session = Depends(get_db)):
    """Validate document format quality (fonts, styles, layout, page setup)."""
    from core.document.validator import validate_document as run_validate

    doc = svc.get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        result = run_validate(doc.file_path)
        return result.to_dict()
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"验证失败: {str(e)}")
