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
from core.document.converter import is_convertible, convert_to_docx

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a .docx / .doc / .wps file."""
    filename = file.filename or "upload.docx"
    ext = Path(filename).suffix.lower()

    # 支持 .docx / .doc / .wps 三种格式
    if ext not in (".docx", ".doc", ".wps"):
        raise HTTPException(
            status_code=400,
            detail="仅支持 .docx、.doc、.wps 格式的文档"
        )

    # Check file size (max 10MB recommended, warn if larger)
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)

    if file_size_mb > 50:
        raise HTTPException(
            status_code=400,
            detail="文件过大（超过 50MB）。建议使用 WPS/Word 插件处理大型文档。"
        )

    if file_size_mb > 10:
        logger.warning(f"Large file detected: {filename} ({file_size_mb:.2f} MB)")

    # Save to temp location
    import re
    safe_name = re.sub(r'[^\w一-鿿._-]', '_', filename)
    tmp_dir = TEMP_DIR
    tmp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = tmp_dir / safe_name

    with open(temp_path, "wb") as f:
        f.write(content)

    # .doc / .wps → 自动转换为 .docx
    if ext in (".doc", ".wps"):
        try:
            converted_path = convert_to_docx(temp_path, tmp_dir)
            logger.info(f"格式转换完成: {filename} → {converted_path.name}")
            # 用转换后的 .docx 路径继续后续流程
            temp_path = converted_path
        except RuntimeError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"文档转换失败: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"文档格式转换失败: {str(e)}"
            )

    try:
        doc = svc.upload_document(db, temp_path, file.filename)
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 清理临时文件（upload_document 已复制到 UPLOAD_DIR）
        try:
            if temp_path.exists():
                temp_path.unlink()
        except Exception:
            pass

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


@router.get("/{doc_id}/preview")
async def get_document_preview(doc_id: int, db: Session = Depends(get_db)):
    """Get document data for A4 preview rendering."""
    from core.document.parser import parse_docx

    doc = svc.get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # 优先使用优化后的文件，支持绝对路径和相对路径两种解析
    file_path = None
    if doc.optimized_path:
        p = Path(doc.optimized_path)
        if p.exists():
            file_path = str(p)
        else:
            # 尝试按文件名在 OUTPUT_DIR 中查找（兼容路径变化场景）
            from config import OUTPUT_DIR
            fallback = OUTPUT_DIR / p.name
            if fallback.exists():
                file_path = str(fallback)
    if not file_path:
        file_path = doc.file_path
    if not Path(file_path).exists():
        raise HTTPException(status_code=404, detail="Document file not found")

    try:
        model = parse_docx(file_path)
        paragraphs = []
        for p in model.paragraphs:
            font_name = None
            font_size_pt = None
            try:
                if p.runs and p.runs[0].format:
                    font_name = getattr(p.runs[0].format, 'font_name', None)
                    font_size_pt = getattr(p.runs[0].format, 'font_size_pt', None)
            except Exception:
                pass

            paragraphs.append({
                "text": p.text or "",
                "role": getattr(p, 'role', None),
                "is_heading": p.is_heading,
                "heading_level": p.heading_level,
                "format": {
                    "alignment": p.format.alignment,
                    "first_line_indent_pt": p.format.first_line_indent_pt,
                    "font_name": font_name,
                    "font_size_pt": font_size_pt,
                    "line_spacing_pt": p.format.line_spacing_pt,
                },
            })
        return {
            "paragraphs": paragraphs,
            "page_setup": {
                "margin_top_mm": model.page_setup.margin_top_mm or 37,
                "margin_bottom_mm": model.page_setup.margin_bottom_mm or 35,
                "margin_left_mm": model.page_setup.margin_left_mm or 28,
                "margin_right_mm": model.page_setup.margin_right_mm or 26,
            },
        }
    except Exception as e:
        logger.error(f"Preview generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"预览生成失败: {str(e)}")
