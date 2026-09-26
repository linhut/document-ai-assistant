# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""
Check API routes: format checking and issue management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from api.schemas.api_models import CheckRequest, CheckResultResponse, CheckIssueResponse, IssueActionRequest
from services import document_service as svc

router = APIRouter()


@router.post("/{doc_id}", response_model=CheckResultResponse)
async def run_check(doc_id: int, req: CheckRequest | None = None, db: Session = Depends(get_db)):
    """Run format checks on a document."""
    doc_type = req.document_type if req else None
    try:
        result = svc.check_document(db, doc_id, doc_type)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        from utils.logger import logger

        logger.error(f"Check failed for doc {doc_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="文档检查失败，请稍后重试")

    issues = svc.get_check_results(db, doc_id)
    return CheckResultResponse(
        document_id=result["document_id"],
        total_issues=result["total_issues"],
        p0_count=result["p0_count"],
        p1_count=result["p1_count"],
        p2_count=result["p2_count"],
        issues=[
            CheckIssueResponse(
                id=i.id,
                check_type=i.check_type,
                severity=i.severity,
                rule_id=i.rule_id,
                location=i.location,
                original_text=i.original_text,
                suggested_fix=i.suggested_fix,
                reason=i.reason,
                standard_ref=i.standard_ref,
                status=i.status,
            )
            for i in issues
        ],
    )


@router.get("/{doc_id}/results", response_model=list[CheckIssueResponse])
async def get_results(doc_id: int, db: Session = Depends(get_db)):
    """Get check results for a document."""
    issues = svc.get_check_results(db, doc_id)
    return [
        CheckIssueResponse(
            id=i.id,
            check_type=i.check_type,
            severity=i.severity,
            rule_id=i.rule_id,
            location=i.location,
            original_text=i.original_text,
            suggested_fix=i.suggested_fix,
            reason=i.reason,
            standard_ref=i.standard_ref,
            status=i.status,
        )
        for i in issues
    ]


@router.put("/{doc_id}/issues/{issue_id}")
async def update_issue(
    doc_id: int,
    issue_id: int,
    req: IssueActionRequest,
    db: Session = Depends(get_db),
):
    """Accept or dismiss a check issue."""
    status_map = {"accept": "accepted", "dismiss": "dismissed"}
    new_status = status_map.get(req.action)
    if not new_status:
        raise HTTPException(status_code=400, detail="action must be 'accept' or 'dismiss'")
    ok = svc.update_issue_status(db, issue_id, new_status)
    if not ok:
        raise HTTPException(status_code=404, detail="Issue not found")
    return {"status": new_status}


@router.post("/dark-bid/{doc_id}")
async def dark_bid_check(doc_id: int, db: Session = Depends(get_db)):
    from utils.logger import logger

    """暗标/标书合规检查：身份信息泄露扫描（命中片段一律脱敏输出）。"""
    from core.compliance.dark_bid import dark_bid_check as run_scan
    from core.document.parser import parse_docx

    doc = svc.get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    try:
        model = parse_docx(doc.file_path)
        issues = run_scan(model)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Dark-bid check failed for doc {doc_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="暗标合规检查失败，请稍后重试")

    return {
        "document_id": doc_id,
        "total_issues": len(issues),
        "issues": [
            {
                "rule_id": i.rule_id,
                "severity": i.severity,
                "name": i.name,
                "location": i.location,
                "original_text": i.original_text,
                "suggested_fix": i.suggested_fix,
                "reason": i.reason,
            }
            for i in issues
        ],
    }
