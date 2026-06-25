# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Abstract base class for AI providers.
All provider implementations must inherit from AIProvider.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AIAnalysisResult:
    """Unified result from AI analysis."""
    issues: list[dict[str, Any]] = field(default_factory=list)
    raw_response: str = ""


class AIProvider(ABC):
    """
    Abstract AI provider interface.
    Implementations must provide: analyze, proofread, rewrite.
    """

    name: str = "base"

    def __init__(self, api_key: str, base_url: str = "", model: str = "", **kwargs):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.extra = kwargs

    @abstractmethod
    async def analyze(self, document_text: str) -> AIAnalysisResult:
        """Analyze a document and return structured issues."""
        ...

    @abstractmethod
    async def proofread(self, text: str) -> list[dict[str, Any]]:
        """Proofread text for typos and punctuation errors."""
        ...

    @abstractmethod
    async def rewrite(self, text: str, context: str = "") -> str:
        """Suggest an improved version of the text."""
        ...

    async def test_connection(self) -> bool:
        """Test if the provider can be reached. Default: try a minimal request."""
        try:
            result = await self.proofread("测试连接")
            return True
        except Exception:
            return False
