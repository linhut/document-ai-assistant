# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
DeepSeek Provider implementation (OpenAI-compatible).
"""
from ai.providers.openai_provider import OpenAIProvider


class DeepSeekProvider(OpenAIProvider):
    """DeepSeek AI provider (uses OpenAI-compatible API)."""

    name = "deepseek"

    def __init__(self, api_key: str, base_url: str = "", model: str = "", **kwargs):
        base_url = base_url or "https://api.deepseek.com/v1"
        model = model or "deepseek-chat"
        super().__init__(api_key, base_url, model, **kwargs)
