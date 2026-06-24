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
