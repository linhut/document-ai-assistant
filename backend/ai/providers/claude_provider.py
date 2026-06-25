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

    async def analyze(self, document_text: str) -> AIAnalysisResult:
        system = "你是公文格式专家。分析文档返回 JSON 格式的 issues 列表。"
        prompt = f"分析以下公文文档，检查格式规范、表达准确性、逻辑完整性：\n\n{document_text[:2000]}\n\n返回 JSON: {{\"issues\": [{{\"type\":\"...\", \"location\":\"...\", \"original\":\"...\", \"suggestion\":\"...\", \"reason\":\"...\", \"severity\":\"high/medium/low\"}}]}}"
        result = await self._call_api([{"role": "user", "content": prompt}], system=system)
        try:
            data = json.loads(result)
            return AIAnalysisResult(issues=data.get("issues", []), raw_response=result)
        except json.JSONDecodeError:
            return AIAnalysisResult(issues=[{"type": "AI分析", "suggestion": result, "severity": "low"}], raw_response=result)

    async def proofread(self, text: str) -> list[dict[str, Any]]:
        prompt = f"检查以下文本的错别字和标点问题，返回 JSON 数组：\n{text[:1000]}"
        result = await self._call_api([{"role": "user", "content": prompt}], temperature=0.1)
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return []

    async def rewrite(self, text: str, context: str = "") -> str:
        prompt = f"优化以下公文文本表达，保持原意，使用规范公文表达：\n{text}\n上下文：{context or '无'}"
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
