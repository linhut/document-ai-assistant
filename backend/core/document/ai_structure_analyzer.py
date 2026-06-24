"""
AI Structure Analyzer — 基于AI的文档结构智能分析

参考 AIPoliDoc 的AI分类方案：
- 提取段落文本（前80字符）
- 发送给AI模型进行语义分类
- 返回结构化分类结果，更新DocumentModel的标题/正文标记

适用场景：未排版文档、格式混乱的文档，本地启发式检测不足时自动触发。
"""
from __future__ import annotations
import json
import re
from typing import Any

from core.document.models import DocumentModel
from utils.logger import logger


# 分类提示词模板
_CLASSIFY_PROMPT = """你是一个中文公文格式分析专家。请分析以下文档段落，判断每个段落的结构类型。

文档段落列表（序号从0开始）：
{paragraphs}

分类规则：
1. doc_title — 公文标题。特征：短文本（通常<30字），无句末标点，常含"关于…的通知/请示/报告/方案/意见"等
2. heading_1 — 一级标题。特征：以"一、""二、""三、"等中文数字开头
3. heading_2 — 二级标题。特征：以"（一）""（二）"等带括号中文数字开头
4. heading_3 — 三级标题。特征：以"1.""2.""3."等阿拉伯数字开头
5. signature — 落款/署名。特征：通常是文档末尾的单位名称、日期
6. body — 正文。以上都不是的段落

请严格按以下JSON格式返回，不要包含其他文字：
[{{"id": 0, "type": "doc_title"}}, {{"id": 1, "type": "body"}}, ...]

重要：
- 只返回JSON数组，不要有任何解释文字
- type必须是上述6种之一
- 每个段落都要有对应的分类结果"""


def classify_with_ai(model: DocumentModel, provider_name: str = "openai") -> bool:
    """
    使用AI模型对文档段落进行语义分类。

    Args:
        model: 文档模型（将被原地修改）
        provider_name: AI提供商名称

    Returns:
        True if classification was applied, False if skipped/failed
    """
    try:
        from ai.manager import create_provider
        from db.session import get_db_session
        from db.models import AIConfig
    except ImportError as e:
        logger.warning(f"AI structure analyzer dependencies not available: {e}")
        return False

    # 获取AI provider
    try:
        from utils.crypto import decrypt_value
        db = next(get_db_session())
        config = db.query(AIConfig).filter(
            AIConfig.provider == provider_name,
            AIConfig.is_active == True
        ).first()
        if not config:
            logger.info(f"No active AI config for {provider_name}, skipping AI structure analysis")
            return False

        api_key = decrypt_value(config.api_key_encrypted) if config.api_key_encrypted else ""
        provider = create_provider(
            provider_name,
            api_key=api_key,
            base_url=config.base_url or "",
            model=config.model or "",
        )
    except Exception as e:
        logger.warning(f"Failed to create AI provider for structure analysis: {e}")
        return False

    # 提取段落文本
    paragraphs_text = []
    for i, para in enumerate(model.paragraphs):
        text = para.text.strip()
        if not text:
            continue
        # 截取前80字符（参考AIPoliDoc的优化模式）
        truncated = text[:80] + ("..." if len(text) > 80 else "")
        paragraphs_text.append(f"{i}: {truncated}")

    if len(paragraphs_text) < 3:
        logger.info("Too few paragraphs for AI structure analysis")
        return False

    # 构建提示词
    prompt = _CLASSIFY_PROMPT.format(paragraphs="\n".join(paragraphs_text))

    # 调用AI
    try:
        logger.info(f"Calling AI ({provider_name}) for structure analysis of {len(paragraphs_text)} paragraphs")
        result = provider.analyze(prompt, task_type="classification")
        raw_response = result.raw_response if hasattr(result, 'raw_response') else str(result)
    except Exception as e:
        logger.error(f"AI structure analysis failed: {e}")
        return False

    # 解析AI返回的JSON
    classifications = _parse_ai_response(raw_response)
    if not classifications:
        logger.warning("Failed to parse AI structure classification response")
        return False

    # 应用分类结果到DocumentModel
    _apply_classifications(model, classifications)
    return True


def _parse_ai_response(raw: str) -> list[dict] | None:
    """
    解析AI返回的JSON分类结果。

    包含5层容错策略（参考AIPoliDoc的JSON修复方案）：
    1. 直接解析
    2. 提取```json```代码块
    3. 提取[...]数组
    4. 修复常见JSON错误（尾逗号、缺失逗号）
    5. 逐行解析
    """
    if not raw:
        return None

    # 策略1: 直接解析
    try:
        data = json.loads(raw.strip())
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass

    # 策略2: 提取```json```代码块
    code_block = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', raw, re.DOTALL)
    if code_block:
        try:
            data = json.loads(code_block.group(1).strip())
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

    # 策略3: 提取[...]数组
    array_match = re.search(r'\[.*\]', raw, re.DOTALL)
    if array_match:
        text = array_match.group(0)
        # 策略4: 修复常见JSON错误
        text = re.sub(r',\s*]', ']', text)  # 尾逗号
        text = re.sub(r',\s*}', '}', text)  # 对象尾逗号
        text = re.sub(r'}\s*{', '},{', text)  # 缺失逗号
        try:
            data = json.loads(text)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

    # 策略5: 逐行提取 {"id": N, "type": "..."} 对象
    objects = re.findall(r'\{[^{}]*"id"\s*:\s*\d+[^{}]*"type"\s*:\s*"[^"]+"[^{}]*\}', raw)
    if objects:
        result = []
        for obj_str in objects:
            try:
                obj = json.loads(obj_str)
                if "id" in obj and "type" in obj:
                    result.append(obj)
            except json.JSONDecodeError:
                continue
        if result:
            return result

    return None


def _apply_classifications(model: DocumentModel, classifications: list[dict]) -> None:
    """将AI分类结果应用到DocumentModel的段落上。"""
    type_to_heading = {
        "doc_title": (True, 0),
        "heading_1": (True, 1),
        "heading_2": (True, 2),
        "heading_3": (True, 3),
        "body": (False, None),
        "signature": (False, None),  # signature不标记为heading
    }

    applied = 0
    for item in classifications:
        try:
            idx = int(item.get("id", -1))
            ptype = str(item.get("type", "")).strip()
        except (ValueError, TypeError):
            continue

        if 0 <= idx < len(model.paragraphs) and ptype in type_to_heading:
            is_heading, level = type_to_heading[ptype]
            # 只更新原本未被启发式检测命中的段落（避免覆盖高置信度检测）
            para = model.paragraphs[idx]
            if not para.is_heading and para.text.strip():
                para.is_heading = is_heading
                para.heading_level = level
                applied += 1

    logger.info(f"AI structure classification applied: {applied} paragraphs updated")


def should_use_ai_analysis(model: DocumentModel) -> bool:
    """
    判断是否需要AI辅助分析。

    触发条件（满足任一）：
    1. 未检测到任何标题
    2. 标题数 < 正文段落数的10%（过少）
    3. 未检测到公文标题(level=0)
    """
    headings = [p for p in model.paragraphs if p.is_heading]
    non_empty = [p for p in model.paragraphs if p.text.strip()]

    if not headings:
        return True
    if len(headings) < max(1, len(non_empty) * 0.1):
        return True
    if not any(p.heading_level == 0 for p in headings):
        return True

    return False
