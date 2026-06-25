# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Custom Provider for any OpenAI-compatible API.
"""
from ai.providers.openai_provider import OpenAIProvider


class CustomProvider(OpenAIProvider):
    """Custom AI provider for any OpenAI-compatible API."""

    name = "custom"

    def __init__(self, api_key: str, base_url: str = "", model: str = "", **kwargs):
        """
        Initialize custom provider.

        Args:
            api_key: API key
            base_url: Full base URL (e.g., https://api.example.com/v1)
            model: Model name
        """
        if not base_url:
            raise ValueError("Custom provider requires base_url")
        if not model:
            raise ValueError("Custom provider requires model")
        super().__init__(api_key, base_url, model, **kwargs)
