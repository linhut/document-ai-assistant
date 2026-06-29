# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Claude Provider (Anthropic).
Uses Anthropic Messages API.
"""
import json
import httpx
from typing import Any
from ai.base import AIProvider, AIAnalysisResult
from utils.logger import logger


# 文档类型中文名映射（与 OpenAIProvider 保持一致）
_TYPE_NAMES = {
    "notice": "通知", "announcement": "公告", "report": "报告",
    "request": "请示", "reply": "批复", "instruction": "意见",
    "decision": "决定", "resolution": "决议", "command": "命令",
    "bill": "议案", "minutes": "会议纪要", "meeting": "会议纪要",
    "communique": "公报", "regulation": "条例", "work_plan": "工作方案",
    "summary": "总结", "letter": "函", "bulletin": "通报",
    "notice_public": "公示", "opinion": "意见", "table_sign": "签发单",
}


class ClaudeProvider(AIProvider):
    """Anthropic Claude provider."""

    name = "claude"

    def __init__(self, api_key: str, base_url: str = "", model: str = "", **kwargs):
        super().__init__(api_key, base_url, model, **kwargs)
        self.base_url = base_url or "https://api.anthropic.com"
        self.model = model or "claude-sonnet-4-20250514"
        self.max_retries = kwargs.get("max_retries", 3)
        self.timeout = kwargs.get("timeout", 60.0)
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            timeout=httpx.Timeout(self.timeout, connect=10.0),
        )

    async def _call_api(self, messages: list[dict], system: str = "",
                         temperature: float = 0.3, max_tokens: int = 2000) -> str:
        import asyncio
        last_error = None
        for attempt in range(self.max_retries):
            try:
                payload: dict[str, Any] = {
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": messages,
                }
                if system:
                    payload["system"] = system

                response = await self.client.post("/v1/messages", json=payload)
                response.raise_for_status()
                data = response.json()
                return data["content"][0]["text"]
            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                last_error = e
                if status in (429, 500, 502, 503) and attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise Exception(f"Claude API error {status}: {e.response.text[:200]}")
            except httpx.ConnectError:
                raise Exception(f"无法连接到 Claude API ({self.base_url})")
            except httpx.TimeoutException:
                raise Exception(f"Claude API 超时 ({self.timeout}s)")
        raise Exception(f"Claude API 调用失败: {last_error}")

    async def analyze(self, document_text: str, **kwargs) -> AIAnalysisResult:
        """Analyze a document for formatting issues, with optional document_type awareness."""
        document_type = kwargs.get("document_type", "notice")
        type_name = _TYPE_NAMES.get(document_type, document_type)

        system = "你是公文格式专家。分析文档返回 JSON 格式的 issues 列表。只返回JSON，不要解释文字。"
        prompt = (
            f"分析以下【{type_name}】公文文档，检查格式规范、表达准确性、逻辑完整性：\n\n"
            f"{document_text[:3000]}\n\n"
            '返回 JSON: {"issues": [{"type":"...", "location":"...", "original":"...", '
            '"suggestion":"...", "reason":"...", "severity":"high/medium/low"}]}'
        )
        result = await self._call_api([{"role": "user", "content": prompt}], system=system)

        # 多策略 JSON 解析（与 OpenAIProvider 保持一致）
        return self._parse_analyze_response(result)

    @staticmethod
    def _parse_analyze_response(raw: str) -> AIAnalysisResult:
        """Robust JSON parsing with multiple fallback strategies."""
        import re
        try:
            data = json.loads(raw)
            if isinstance(data, dict) and "issues" in data:
                return AIAnalysisResult(issues=data["issues"], raw_response=raw)
        except json.JSONDecodeError:
            pass
        m = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', raw, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(1).strip())
                if isinstance(data, dict) and "issues" in data:
                    return AIAnalysisResult(issues=data["issues"], raw_response=raw)
            except json.JSONDecodeError:
                pass
        m = re.search(r'\{[\s\S]*"issues"\s*:[\s\S]*\}', raw)
        if m:
            try:
                candidate = re.sub(r',\s*([}\]])', r'\1', m.group(0))
                data = json.loads(candidate)
                if isinstance(data, dict) and "issues" in data:
                    return AIAnalysisResult(issues=data["issues"], raw_response=raw)
            except json.JSONDecodeError:
                pass
        return AIAnalysisResult(
            issues=[{"type": "AI分析", "location": "全文", "original": "",
                     "suggestion": raw[:500], "reason": "AI 综合建议", "severity": "low"}],
            raw_response=raw,
        )

    async def proofread(self, text: str) -> list[dict[str, Any]]:
        prompt = f"检查以下文本的错别字和标点问题，返回 JSON 数组：\n{text[:1000]}"
        result = await self._call_api([{"role": "user", "content": prompt}], temperature=0.1)
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return []

    async def rewrite(self, text: str, context: str = "") -> str:
        """Rewrite/rewrite text for official document style.

        If context is non-empty, it is treated as the FULL prompt (including instructions).
        If context is empty, a default rewrite prompt is used.
        """
        if context:
            # context 包含完整指令时直接作为用户消息
            prompt = context
        else:
            prompt = (
                "优化以下公文文本表达，保持原意，使用规范公文表达：\n"
                f"{text}\n"
                "只返回优化后的文本，不要解释。"
            )
        return await self._call_api([{"role": "user", "content": prompt}])

    async def test_connection(self) -> bool:
        try:
            await self._call_api([{"role": "user", "content": "回复：OK"}], max_tokens=10)
            return True
        except Exception as e:
            logger.error(f"Claude connection test failed: {e}")
            return False

    async def close(self):
        await self.client.aclose()
