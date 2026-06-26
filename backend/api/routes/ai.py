# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
AI API routes: AI-powered analysis and suggestions.
支持多模型管理、模型列表获取、连接测试。
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from db.database import get_db
from db.models import AIConfig
from ai.manager import (
    create_provider, available_providers, fetch_models,
    get_default_config, mask_api_key,
)
from services import document_service as doc_svc
from api.schemas.api_models import ApplyAIRequest
from utils.logger import logger
from utils.crypto import encrypt_value, decrypt_value

router = APIRouter()


class AIConfigRequest(BaseModel):
    provider: str
    api_key: str = ""
    base_url: str = ""
    model: str = ""
    is_active: bool | None = None


class AITestRequest(BaseModel):
    provider: str
    api_key: str
    base_url: str = ""
    model: str = ""


class FetchModelsRequest(BaseModel):
    base_url: str
    api_key: str
    provider: str = "custom"


@router.get("/providers")
async def list_ai_providers():
    """List available AI providers with their default configs."""
    default = get_default_config()
    default["api_key"] = mask_api_key(default["api_key"])
    return {
        "providers": available_providers(),
        "default": default,
    }


@router.get("/status")
async def get_ai_model_status():
    """获取所有已配置 AI 模型的可用性状态（每 60 秒自动检测）。"""
    from services.model_health import get_all_statuses
    statuses = get_all_statuses()
    return {"statuses": statuses, "total": len(statuses)}


@router.post("/config")
async def save_ai_config(req: AIConfigRequest, db: Session = Depends(get_db)):
    """Save AI provider configuration. API key is encrypted before storage."""
    try:
        config = db.query(AIConfig).filter(AIConfig.provider == req.provider).first()

        if config:
            # 更新已有配置 — 仅更新非空字段
            if req.api_key:
                config.api_key_encrypted = encrypt_value(req.api_key)
            if req.base_url:
                config.base_url = req.base_url
            if req.model:
                config.model = req.model
            if req.is_active is not None:
                config.is_active = req.is_active
        else:
            # 新建配置
            if not req.api_key:
                raise HTTPException(status_code=400, detail="新建配置时必须提供 API Key")
            config = AIConfig(
                provider=req.provider,
                api_key_encrypted=encrypt_value(req.api_key),
                base_url=req.base_url,
                model=req.model,
                is_active=req.is_active if req.is_active is not None else True,
            )
            db.add(config)

        db.commit()
        logger.info(f"AI config saved: {req.provider}")

        return {"success": True, "message": "配置保存成功"}
    except Exception as e:
        logger.error(f"Save AI config failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/{provider}")
async def get_ai_config(provider: str, db: Session = Depends(get_db)):
    """Get AI provider configuration (API key masked)."""
    config = db.query(AIConfig).filter(AIConfig.provider == provider).first()

    if not config:
        # 返回默认配置
        default = get_default_config()
        if provider == default["provider"]:
            return {
                "exists": False,
                "default": {
                    **default,
                    "api_key_masked": mask_api_key(default["api_key"]),
                },
                "message": "使用内置默认配置",
            }
        return {"exists": False}

    # 脱敏返回
    return {
        "exists": True,
        "provider": config.provider,
        "base_url": config.base_url,
        "model": config.model,
        "is_active": config.is_active,
        "api_key_masked": mask_api_key(decrypt_value(config.api_key_encrypted) or ""),
    }


def _resolve_api_key(api_key: str, provider: str, db: Session) -> str:
    """解析 API Key：__saved__ 占位符从数据库读取已保存的密钥。"""
    if api_key == "__saved__":
        config = db.query(AIConfig).filter(AIConfig.provider == provider).first()
        if config and config.api_key_encrypted:
            try:
                resolved = decrypt_value(config.api_key_encrypted)
                if resolved:
                    return resolved
            except Exception as e:
                logger.error(f"Failed to decrypt saved key: {e}")
        # 回退到默认
        return get_default_config()["api_key"]
    return api_key


@router.post("/test")
async def test_ai_connection(req: AITestRequest, db: Session = Depends(get_db)):
    """Test AI provider connection with detailed error classification."""
    try:
        resolved_key = _resolve_api_key(req.api_key, req.provider, db)
        provider = create_provider(req.provider, resolved_key, req.base_url, req.model)
        success = await provider.test_connection()

        if success:
            return {
                "success": True,
                "message": "连接成功",
                "provider": req.provider,
                "model": req.model or "default",
                "base_url": req.base_url,
            }
        else:
            return {
                "success": False,
                "message": "连接失败，请检查配置",
                "provider": req.provider,
            }
    except ValueError as e:
        return {"success": False, "message": f"配置错误: {str(e)}", "error_type": "config"}
    except Exception as e:
        error_msg = str(e)
        # 分类错误信息
        if "401" in error_msg or "认证" in error_msg:
            error_type = "auth"
            user_msg = "API Key 无效或已过期"
        elif "403" in error_msg or "拒绝" in error_msg:
            error_type = "permission"
            user_msg = "访问被拒绝，请检查 API Key 权限"
        elif "404" in error_msg:
            error_type = "endpoint"
            user_msg = "API 端点不存在，请检查 Base URL"
        elif "超时" in error_msg or "timeout" in error_msg.lower():
            error_type = "timeout"
            user_msg = "连接超时，请检查网络或 Base URL"
        elif "连接" in error_msg or "connect" in error_msg.lower():
            error_type = "network"
            user_msg = "无法连接到服务器，请检查 Base URL 和网络"
        else:
            error_type = "unknown"
            user_msg = f"连接失败: {error_msg[:100]}"

        logger.error(f"AI connection test failed ({error_type}): {e}")
        return {
            "success": False,
            "message": user_msg,
            "error_type": error_type,
            "provider": req.provider,
        }


@router.post("/models")
async def get_models(req: FetchModelsRequest, db: Session = Depends(get_db)):
    """Fetch available models from an API endpoint."""
    try:
        resolved_key = _resolve_api_key(req.api_key, req.provider, db)
        models = await fetch_models(req.base_url, resolved_key)
        return {
            "success": True,
            "models": models,
            "count": len(models),
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "models": [],
        }


@router.get("/default")
async def get_default_ai_config():
    """Get default AI configuration (API key masked)."""
    default = get_default_config()
    default["api_key"] = mask_api_key(default["api_key"])
    return default


@router.post("/analyze/{doc_id}")
async def ai_analyze(doc_id: int, provider: str = "openai", document_type: str = "", db: Session = Depends(get_db)):
    """Run AI analysis on a document."""
    doc = doc_svc.get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # 确定文档类型：参数 > 数据库记录 > 默认 notice
    doc_type = document_type or doc.document_type or "notice"

    # 获取 provider 配置
    config = db.query(AIConfig).filter(AIConfig.provider == provider).first()
    if not config:
        # 使用默认配置
        default = get_default_config()
        api_key = default["api_key"]
        base_url = default["base_url"]
        model = default["model"]
        provider_name = default["provider"]
    else:
        api_key = decrypt_value(config.api_key_encrypted) or ""
        base_url = config.base_url
        model = config.model
        provider_name = config.provider

    try:
        # 解析文档内容
        from core.document.parser import parse_docx
        doc_model = parse_docx(doc.file_path)
        doc_text = "\n".join([p.text for p in doc_model.paragraphs if p.text.strip()])

        # 调用 AI
        ai_provider = create_provider(provider_name, api_key, base_url, model)
        result = await ai_provider.analyze(doc_text, document_type=doc_type)

        return {
            "success": True,
            "provider": provider_name,
            "issues": result.issues,
            "raw_response": result.raw_response,
        }
    except Exception as e:
        logger.error(f"AI analyze failed: {e}")
        return {
            "success": False,
            "message": f"AI 分析失败: {str(e)[:100]}",
        }


@router.post("/apply/{doc_id}")
async def apply_ai_suggestions(doc_id: int, req: ApplyAIRequest, db: Session = Depends(get_db)):
    """将用户选中的 AI 建议应用到文档，生成优化后的 .docx。"""
    from core.document.parser import parse_docx
    from core.document.generator import generate_docx
    from config import OUTPUT_DIR
    from pathlib import Path

    doc = doc_svc.get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档未找到")

    if not req.suggestions:
        raise HTTPException(status_code=400, detail="未选择任何建议")

    # 解析文档
    try:
        doc_model = parse_docx(doc.file_path)
    except Exception as e:
        logger.error(f"parse_docx failed for doc {doc_id}: {e}")
        raise HTTPException(status_code=500, detail=f"文档解析失败: {str(e)[:100]}")

    # 逐条应用建议：在段落文本中做原文替换
    applied = 0
    for sug in req.suggestions:
        original = sug.original.strip()
        suggestion = sug.suggestion.strip()
        if not original or not suggestion or original == suggestion:
            continue
        for para in doc_model.paragraphs:
            if original in para.text:
                for run in para.runs:
                    if original in run.text:
                        run.text = run.text.replace(original, suggestion, 1)
                        applied += 1
                        break
                else:
                    # 跨 run 的情况：拼接后替换
                    full = para.text
                    if original in full:
                        new_full = full.replace(original, suggestion, 1)
                        if para.runs:
                            para.runs[0].text = new_full
                            for r in para.runs[1:]:
                                r.text = ""
                        applied += 1
                break  # 每条建议只替换第一处

    if applied == 0:
        return {
            "success": False,
            "message": "未能匹配到任何原文片段，建议可能已不适用于当前文档",
        }

    # 生成优化文档
    out_name = Path(doc.filename).stem + "_ai_optimized.docx"
    out_path = OUTPUT_DIR / out_name
    try:
        generate_docx(doc_model, str(out_path))
    except Exception as e:
        logger.error(f"generate_docx failed: {e}")
        raise HTTPException(status_code=500, detail=f"文档生成失败: {str(e)[:100]}")

    # 更新 DB
    try:
        doc.status = "optimized"
        doc.optimized_path = str(out_path)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to update doc {doc_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="数据库更新失败")

    logger.info(f"AI suggestions applied: doc={doc_id}, applied={applied}/{len(req.suggestions)}")
    return {
        "success": True,
        "applied_count": applied,
        "total_suggestions": len(req.suggestions),
        "output_path": str(out_path),
        "message": f"已成功应用 {applied} 项 AI 建议",
    }