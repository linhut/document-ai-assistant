"""
OpenAI Provider implementation.
"""
import json
import httpx
from typing import Any

from ai.base import AIProvider, AIAnalysisResult
from utils.logger import logger


class OpenAIProvider(AIProvider):
    """OpenAI GPT-based AI provider with retry logic."""

    name = "openai"

    def __init__(self, api_key: str, base_url: str = "", model: str = "", **kwargs):
        super().__init__(api_key, base_url, model, **kwargs)
        self.base_url = base_url or "https://api.openai.com/v1"
        self.model = model or "gpt-4o-mini"
        self.max_retries = kwargs.get("max_retries", 5)
        self.timeout = kwargs.get("timeout", 60.0)
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=httpx.Timeout(self.timeout, connect=10.0),
        )

    async def _call_api(
        self, messages: list[dict], temperature: float = 0.3, max_tokens: int = 2000
    ) -> str:
        """
        Call OpenAI Chat Completions API with exponential backoff retry.

        Retry strategy: 2s → 4s → 8s → 16s → 32s for transient errors (429, 500, 502, 503).
        Non-retryable errors (401, 403, 404) raise immediately.
        """
        import asyncio
        import random

        last_error: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                response = await self.client.post(
                    "/chat/completions",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                )

                if response.status_code == 401:
                    raise Exception("API 认证失败：API Key 无效或已过期")
                if response.status_code == 403:
                    raise Exception("API 访问被拒绝：无权访问该模型")
                if response.status_code == 404:
                    raise Exception(f"API 端点不存在：{self.base_url}")
                if response.status_code == 429:
                    last_error = Exception(f"API 限流 (HTTP 429)")
                    wait = min(2 ** (attempt + 1), 32) + random.uniform(0, 1)
                    logger.warning(f"Rate limited (attempt {attempt + 1}/{self.max_retries}), waiting {wait:.1f}s")
                    await asyncio.sleep(wait)
                    continue

                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                if not content or not content.strip():
                    raise Exception("API 返回空内容，请稍后重试")
                return content

            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                if status in (429, 500, 502, 503):
                    last_error = e
                    wait = min(2 ** (attempt + 1), 32) + random.uniform(0, 1)
                    logger.warning(f"HTTP {status} (attempt {attempt + 1}/{self.max_retries}), retrying in {wait:.1f}s")
                    await asyncio.sleep(wait)
                    continue
                logger.error(f"OpenAI API HTTP error: {status} - {e.response.text}")
                raise Exception(f"API 调用失败 (HTTP {status}): {e.response.text[:200]}")

            except httpx.ConnectError as e:
                last_error = Exception(f"无法连接到 API 服务器: {self.base_url}")
                logger.warning(f"Connect error (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue

            except httpx.ReadTimeout as e:
                last_error = Exception(f"API 请求超时（{self.timeout}秒）")
                logger.warning(f"Read timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2)
                    continue

            except Exception as e:
                logger.error(f"OpenAI API call failed: {e}")
                raise Exception(f"API 调用失败: {str(e)}")

        # All retries exhausted
        raise Exception(
            f"API 调用失败（已重试 {self.max_retries} 次）: {last_error or '未知错误，请检查网络或 API 配额'}"
        )

    async def analyze(self, document_text: str, document_type: str = "notice") -> AIAnalysisResult:
        """Analyze document against GB/T 9704 official document standards, type-aware."""

        # 文档类型中文名映射
        TYPE_NAMES = {
            "notice": "通知", "announcement": "公告", "report": "报告",
            "request": "请示", "reply": "批复", "instruction": "意见",
            "decision": "决定", "resolution": "决议", "command": "命令",
            "bill": "议案", "minutes": "会议纪要", "meeting": "会议纪要",
            "communique": "公报", "regulation": "条例", "work_plan": "工作方案",
            "summary": "总结", "letter": "函", "bulletin": "通报",
            "notice_public": "公示", "opinion": "意见", "table_sign": "签发单",
        }
        type_name = TYPE_NAMES.get(document_type, document_type)

        # 按文档类型定制检查重点
        TYPE_SPECIFIC_RULES = {
            "minutes": """【会议纪要特殊规则】
- 编号段落（1. 2. 3.）是议题条目，不是标题，不需要首行缩进
- 日期可用阿拉伯数字（2026年6月23日），不需要改为汉字大写
- "XX同志："是发言人标记，按标题处理
- 正文是具体发言和议定内容，需要首行缩进2字符""",
            "report": """【报告特殊规则】
- 标题格式："关于XXX的报告"
- 结尾用"特此报告"或"以上报告，请审阅"
- 不得有"请批复"等请示用语""",
            "request": """【请示特殊规则】
- 标题格式："关于XXX的请示"
- 结尾必须用"妥否，请批示"或"以上请示，请批复"
- 一文一事，不得多事一请""",
            "notice": """【通知特殊规则】
- 标题格式："关于XXX的通知"
- 正文首行缩进2字符
- 结尾用"特此通知"
- 日期用汉字大写（二〇二六年六月二十三日）""",
        }
        type_rules = TYPE_SPECIFIC_RULES.get(document_type, "")

        prompt = f"""你是公文格式审核专家（GB/T 9704标准）。请逐段检查以下【{type_name}】，针对每个问题单独返回一条。

【通用检查规则】
1. 标题：方正小标宋简体/黑体，二号~小二号，居中
2. 正文字体：仿宋_GB2312，三号（16pt）
3. 正文首行缩进：2字符（2em/32pt）
4. 行距：固定值28~29磅
5. 页边距：上37mm 下35mm 左28mm 右26mm
6. 一级标题：黑体三号，如"一、""二、"
7. 二级标题：楷体三号，如"（一）""（二）"
8. 标点符号：中文全角标点
9. 落款：右对齐

{type_rules}

【文档内容】
{document_text[:3000]}

【返回格式】严格返回JSON，每个问题单独一条：
{{
    "issues": [
        {{
            "type": "字体/字号/缩进/行距/页边距/对齐/标点/日期/文种/结构/其他",
            "location": "第N段或具体位置",
            "original": "原文中有问题的具体文字",
            "suggestion": "建议修改为",
            "reason": "依据说明",
            "severity": "high/medium/low"
        }}
    ],
    "summary": "一句话总体评价"
}}

重要：
1. 每个问题单独一条，不要合并
2. 只报告真正的问题，正确的不要报告
3. 如果文档没有问题，返回空issues数组
4. 根据【{type_name}】的特殊规则判断，不要套用其他文种的规则"""

        messages = [
            {"role": "system", "content": "你是公文格式审核专家，严格按照GB/T 9704标准检查文档。只返回JSON，不要任何解释文字。"},
            {"role": "user", "content": prompt},
        ]
        result = await self._call_api(messages)

        # 多策略JSON解析
        return self._parse_analyze_response(result)

    @staticmethod
    def _parse_analyze_response(raw: str) -> AIAnalysisResult:
        """Robust JSON parsing with multiple fallback strategies."""
        import re

        # Strategy 1: direct JSON parse
        try:
            data = json.loads(raw)
            if isinstance(data, dict) and "issues" in data:
                return AIAnalysisResult(issues=data["issues"], raw_response=raw)
        except json.JSONDecodeError:
            pass

        # Strategy 2: extract JSON from markdown code block
        m = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', raw, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(1).strip())
                if isinstance(data, dict) and "issues" in data:
                    return AIAnalysisResult(issues=data["issues"], raw_response=raw)
            except json.JSONDecodeError:
                pass

        # Strategy 3: find JSON object in text
        m = re.search(r'\{[\s\S]*"issues"\s*:[\s\S]*\}', raw)
        if m:
            try:
                # Fix common JSON errors
                candidate = m.group(0)
                candidate = re.sub(r',\s*([}\]])', r'\1', candidate)  # trailing commas
                data = json.loads(candidate)
                if isinstance(data, dict) and "issues" in data:
                    return AIAnalysisResult(issues=data["issues"], raw_response=raw)
            except json.JSONDecodeError:
                pass

        # Strategy 4: try to find a JSON array of issues directly
        m = re.search(r'\[\s*\{[\s\S]*\}\s*\]', raw)
        if m:
            try:
                candidate = re.sub(r',\s*([}\]])', r'\1', m.group(0))
                issues = json.loads(candidate)
                if isinstance(issues, list) and len(issues) > 0:
                    return AIAnalysisResult(issues=issues, raw_response=raw)
            except json.JSONDecodeError:
                pass

        # Strategy 5: fallback — wrap raw text as a single issue
        logger.warning("AI response is not valid JSON, using raw text as single issue")
        return AIAnalysisResult(
            issues=[{
                "type": "AI分析",
                "location": "全文",
                "original": "",
                "suggestion": raw[:500],
                "reason": "AI 综合建议",
                "severity": "low",
            }],
            raw_response=raw,
        )

    async def proofread(self, text: str) -> list[dict[str, Any]]:
        """Proofread text for typos and errors."""
        prompt = f"""请检查以下文本中的错别字、错误用词和标点符号问题：

{text[:1000]}

返回 JSON 格式：
[
    {{
        "original": "错误词",
        "suggested": "正确词",
        "position": "第X段",
        "reason": "原因",
        "confidence": 0.9
    }}
]
"""
        messages = [{"role": "user", "content": prompt}]
        result = await self._call_api(messages, temperature=0.1)

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            logger.warning("Proofread response is not valid JSON")
            return []

    async def rewrite(self, text: str, context: str = "") -> str:
        """Suggest improved version of text."""
        prompt = f"""请优化以下文本的表达，使其更加规范、简洁、准确：

原文：{text}

上下文：{context if context else "无"}

要求：
1. 保持原意
2. 使用公文规范表达
3. 简洁明了

请直接返回优化后的文本，不要解释。
"""
        messages = [{"role": "user", "content": prompt}]
        return await self._call_api(messages, temperature=0.3)

    async def test_connection(self) -> bool:
        """Test OpenAI API connection."""
        try:
            messages = [{"role": "user", "content": "请回复：连接成功"}]
            await self._call_api(messages, max_tokens=20)
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
