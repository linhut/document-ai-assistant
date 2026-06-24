"""
Plugin Bridge — Office插件本地API适配层

Word/WPS Add-in 通过此桥接层与 Python Core Engine 通信。
职责：
  - 接收插件请求（check / optimize / template）
  - 转换为 Document Engine 调用
  - 返回插件可解析的JSON结果

架构：
  Word/WPS Add-in  →  Plugin Bridge (本文件)  →  Document Engine
"""
from __future__ import annotations
from pathlib import Path
from typing import Any
import tempfile
import os

from core.document.parser import parse_docx
from core.document.generator import generate_docx
from core.rules.engine import RuleEngine
from core.template.style_manager import list_templates, get_template
from core.template.generator import generate_docx_template, generate_dotx_template
from utils.logger import logger

_engine = RuleEngine()


# ---------------------------------------------------------------------------
#  Document Check
# ---------------------------------------------------------------------------

def check_document_from_file(file_path: str, doc_type: str = "notice") -> dict:
    """
    从文件路径检查文档格式。

    Args:
        file_path: .docx 文件路径
        doc_type: 文档类型

    Returns:
        {issues: [...], summary: {...}}
    """
    try:
        model = parse_docx(file_path)
        issues = _engine.check(model, doc_type)

        p0 = sum(1 for i in issues if i.severity == "P0")
        p1 = sum(1 for i in issues if i.severity == "P1")
        p2 = sum(1 for i in issues if i.severity == "P2")

        return {
            "success": True,
            "total_issues": len(issues),
            "summary": {"P0": p0, "P1": p1, "P2": p2},
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
    except Exception as e:
        logger.error(f"Plugin check failed: {e}")
        return {"success": False, "error": str(e)}


def check_document_from_bytes(content: bytes, doc_type: str = "notice") -> dict:
    """
    从内存字节流检查文档（插件直接发送文件内容时使用）。
    """
    tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
    try:
        tmp.write(content)
        tmp.close()
        return check_document_from_file(tmp.name, doc_type)
    finally:
        os.unlink(tmp.name)


# ---------------------------------------------------------------------------
#  Document Optimize
# ---------------------------------------------------------------------------

def optimize_document_from_file(file_path: str, doc_type: str = "notice",
                                 output_path: str | None = None) -> dict:
    """
    优化文档并生成新文件。

    Args:
        file_path: 输入 .docx 路径
        doc_type: 文档类型
        output_path: 输出路径（默认同目录 _optimized.docx）

    Returns:
        {success, output_path, issues_before, issues_after, fixes_applied}
    """
    try:
        model = parse_docx(file_path)

        # Check + Fix
        issues_before, fixed_model = _engine.check_and_fix(model, doc_type)

        # Generate output
        if output_path is None:
            p = Path(file_path)
            output_path = str(p.parent / f"{p.stem}_optimized.docx")

        generate_docx(fixed_model, output_path)

        # Re-check to verify
        issues_after = _engine.check(fixed_model, doc_type)

        return {
            "success": True,
            "output_path": output_path,
            "issues_before": len(issues_before),
            "issues_after": len(issues_after),
            "fixes_applied": len(issues_before) - len(issues_after),
        }
    except Exception as e:
        logger.error(f"Plugin optimize failed: {e}")
        return {"success": False, "error": str(e)}


def optimize_document_from_bytes(content: bytes, doc_type: str = "notice") -> dict:
    """从内存字节流优化文档。"""
    tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
    try:
        tmp.write(content)
        tmp.close()
        result = optimize_document_from_file(tmp.name, doc_type)
        # Read optimized file back
        if result.get("success") and os.path.exists(result["output_path"]):
            with open(result["output_path"], "rb") as f:
                result["output_bytes"] = f.read()
        return result
    finally:
        os.unlink(tmp.name)


# ---------------------------------------------------------------------------
#  Template Operations
# ---------------------------------------------------------------------------

def get_template_list(source: str = "all") -> list[dict]:
    """获取模板列表。"""
    return list_templates(source)


def download_template_docx(template_id: str, output_path: str) -> dict:
    """生成并保存模板 .docx 文件。"""
    try:
        generate_docx_template(template_id, output_path)
        return {"success": True, "output_path": output_path}
    except Exception as e:
        logger.error(f"Template generation failed: {e}")
        return {"success": False, "error": str(e)}


def download_template_dotx(template_id: str, output_path: str) -> dict:
    """生成并保存模板 .dotx 文件。"""
    try:
        generate_dotx_template(template_id, output_path)
        return {"success": True, "output_path": output_path}
    except Exception as e:
        logger.error(f"Dotx generation failed: {e}")
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
#  Health Check
# ---------------------------------------------------------------------------

def health_check() -> dict:
    """插件连接健康检查。"""
    return {
        "status": "ok",
        "engine": "Python Document Engine",
        "version": "0.8.0",
        "features": ["check", "optimize", "templates"],
    }