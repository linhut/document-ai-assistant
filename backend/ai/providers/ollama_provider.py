# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Ollama Provider — 本地大模型。
支持任何兼容 OpenAI API 的本地模型服务。
"""
from ai.providers.openai_provider import OpenAIProvider
from utils.logger import logger


class OllamaProvider(OpenAIProvider):
    """Ollama local model provider (OpenAI-compatible)."""

    name = "ollama"

    def __init__(self, api_key: str = "ollama", base_url: str = "", model: str = "", **kwargs):
        base_url = base_url or "http://localhost:11434/v1"
        model = model or "qwen2.5:7b"
        super().__init__(api_key, base_url, model, **kwargs)
