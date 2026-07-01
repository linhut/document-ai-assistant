# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Document service: business logic for document upload, check, optimize operations.
"""
from __future__ import annotations
import re
import shutil
from pathlib import Path
from sqlalchemy.orm import Session

from config import UPLOAD_DIR, OUTPUT_DIR
from db.models import Document, CheckResult
from core.document.parser import parse_docx
from core.document.generator import generate_docx
from core.rules.engine import RuleEngine
from utils.file_utils import file_sha256
from utils.logger import logger

_rule_engine = RuleEngine()


def clear_rule_cache() -> None:
    """清除规则引擎缓存，供外部模块调用。"""
    _rule_engine.clear_cache()

# 输出文件名后缀
_OPTIMIZED_SUFFIX = "_optimized.docx"

# 文件名→文档类型映射（基于关键词）
_TYPE_KEYWORDS: dict[str, str] = {
    "命令": "command", "令": "command",
    "决定": "decision",
    "公告": "notice_public",
    "通告": "announcement",
    "通知": "notice",
    "通报": "bulletin",
    "议案": "bill",
    "报告": "report",
    "请示": "request",
    "批复": "reply",
    "函": "letter",
    "纪要": "minutes", "会议纪要": "meeting",
    "决议": "resolution",
    "指示": "instruction",
    "制度": "regulation",
    "公报": "communique",
    "意见": "opinion",
    "总结": "summary",
    "方案": "work_plan", "计划": "work_plan",
    "桌签": "table_sign",
    "技术方案": "technical_proposal",
}


def _detect_doc_type(filename: str) -> str:
    """根据文件名关键词推断文档类型，无法识别时返回 'notice'。"""
    stem = Path(filename).stem
    # 按关键词长度降序匹配（"会议纪要" 优先于 "纪要"，"技术方案" 优先于 "方案"）
    for keyword in sorted(_TYPE_KEYWORDS, key=len, reverse=True):
        if keyword in stem:
            return _TYPE_KEYWORDS[keyword]
    return "notice"


def _safe_filename(filename: str) -> str:
    """安全处理文件名，防止路径遍历。保留中文字符。"""
    # 取最后一个路径分隔符之后的部分
    name = Path(filename).name
    # 移除危险字符，保留中文、字母、数字、下划线、点、连字符
    safe = re.sub(r'[^\w一-鿿._-]', '_', name)
    return safe or "upload.docx"


def upload_document(db: Session, file_path: Path, filename: str) -> Document:
    """Upload and register a document in the database."""
    safe_name = _safe_filename(filename)
    dest = UPLOAD_DIR / safe_name

    if not file_path.exists():
        raise FileNotFoundError(f"上传文件不存在: {file_path}")

    shutil.copy2(str(file_path), str(dest))

    doc_hash = file_sha256(dest)

    try:
        model = parse_docx(str(dest))
        paragraph_count = len(model.paragraphs)
    except Exception as e:
        logger.warning(f"parse_docx failed during upload (non-fatal): {e}")
        paragraph_count = 0

    doc = Document(
        filename=safe_name,
        file_path=str(dest),
        file_hash=doc_hash,
        document_type=_detect_doc_type(filename),
        status="uploaded",
        page_count=1,
        paragraph_count=paragraph_count,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    logger.info(f"Document uploaded: {doc.id} - {safe_name}")
    return doc


def get_document(db: Session, doc_id: int) -> Document | None:
    return db.query(Document).filter(Document.id == doc_id).first()


def list_documents(db: Session, skip: int = 0, limit: int = 50) -> list[Document]:
    return db.query(Document).order_by(Document.created_at.desc()).offset(skip).limit(limit).all()


def check_document(db: Session, doc_id: int, doc_type: str | None = None) -> dict:
    """Run rule-based checks on a document. Saves results to DB."""
    doc = get_document(db, doc_id)
    if not doc:
        raise ValueError(f"Document not found: {doc_id}")

    doc_type = doc_type or doc.document_type or "notice"

    try:
        model = parse_docx(doc.file_path)
    except Exception as e:
        logger.error(f"parse_docx failed for doc {doc_id}: {e}")
        raise ValueError(f"文档解析失败，请确认文件格式正确（.docx/.doc/.wps）: {str(e)}")

    # Rule-based checks using RuleEngine
    try:
        issues = _rule_engine.check(model, doc_type)
    except Exception as e:
        logger.error(f"RuleEngine.check failed for doc {doc_id}, type={doc_type}: {e}")
        issues = []

    # Save to DB（带 rollback 保护）
    try:
        db.query(CheckResult).filter(CheckResult.document_id == doc_id).delete()
        p0 = p1 = p2 = 0
        for issue in issues:
            if issue.severity == "P0":
                p0 += 1
            elif issue.severity == "P1":
                p1 += 1
            else:
                p2 += 1
            db.add(CheckResult(
                document_id=doc_id,
                check_type=issue.check_type,
                severity=issue.severity,
                rule_id=issue.rule_id,
                location=issue.location,
                original_text=issue.original_text,
                suggested_fix=issue.suggested_fix,
                reason=issue.reason,
            ))
        doc.status = "checked"
        db.commit()
    except Exception as e:
        logger.error(f"Failed to save check results for doc {doc_id}: {e}")
        db.rollback()
        raise

    logger.info(f"Check complete: {len(issues)} issues found (P0:{p0}, P1:{p1}, P2:{p2})")

    return {
        "document_id": doc_id,
        "total_issues": len(issues),
        "p0_count": p0,
        "p1_count": p1,
        "p2_count": p2,
    }


def get_check_results(db: Session, doc_id: int) -> list[CheckResult]:
    return db.query(CheckResult).filter(CheckResult.document_id == doc_id).all()


def update_issue_status(db: Session, issue_id: int, status: str) -> bool:
    issue = db.query(CheckResult).filter(CheckResult.id == issue_id).first()
    if not issue:
        return False
    issue.status = status
    db.commit()
    return True


def optimize_document(
    db: Session, doc_id: int, doc_type: str | None = None, apply_fixes: bool = True,
    selected_rule_ids: list[str] | None = None,
    header_config: dict | None = None,
    footer_note_config: dict | None = None,
    page_number_config: dict | None = None,
) -> dict:
    """Check + fix a document, then generate the optimized docx."""
    doc = get_document(db, doc_id)
    if not doc:
        raise ValueError(f"Document not found: {doc_id}")

    doc_type = doc_type or doc.document_type or "notice"

    # 解析文档
    try:
        model = parse_docx(doc.file_path)
    except Exception as e:
        logger.error(f"parse_docx failed for doc {doc_id} during optimize: {e}")
        raise ValueError(f"文档解析失败，请确认文件格式正确（.docx/.doc/.wps）: {str(e)}")

    # 规则检查 + 修复
    try:
        if apply_fixes:
            issues, fixed_model = _rule_engine.check_and_fix(model, doc_type, selected_rule_ids)
        else:
            issues = _rule_engine.check(model, doc_type)
            fixed_model = model
    except Exception as e:
        logger.error(f"RuleEngine failed for doc {doc_id}, type={doc_type}: {e}")
        raise ValueError(f"规则引擎处理失败: {str(e)}")

    # 生成优化后的文档（包含doc_id防止文件名冲突）
    out_name = f"{Path(doc.filename).stem}_doc{doc_id}{_OPTIMIZED_SUFFIX}"
    out_path = OUTPUT_DIR / out_name
    try:
        generate_docx(fixed_model, str(out_path))
    except Exception as e:
        logger.error(f"generate_docx failed for doc {doc_id}: {e}")
        raise ValueError(f"文档生成失败: {str(e)}")

    # 版头/版记注入
    try:
        from api.routes.optimize import _inject_header_to_docx, _inject_footer_to_docx, _inject_page_number_to_docx
        if header_config and header_config.get('enabled', True):
            _inject_header_to_docx(str(out_path), header_config)
        if footer_note_config and footer_note_config.get('enabled', True):
            _inject_footer_to_docx(str(out_path), footer_note_config)
        if page_number_config and page_number_config.get('enabled', True):
            _inject_page_number_to_docx(str(out_path), page_number_config)
    except Exception as e:
        logger.warning(f"Header/footer/page-number injection failed (non-fatal): {e}", exc_info=True)

    # 更新数据库（带 rollback 保护）
    try:
        doc.status = "optimized"
        doc.optimized_path = str(out_path)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to update doc {doc_id} status: {e}")
        db.rollback()
        raise

    logger.info(f"Document optimized: {doc_id} -> {out_path} (fixed {len(issues)} issues)")
    return {
        "document_id": doc_id,
        "output_path": str(out_path),
        "output_name": out_name,
        "fixes_applied": len(issues) if apply_fixes else 0,
    }
