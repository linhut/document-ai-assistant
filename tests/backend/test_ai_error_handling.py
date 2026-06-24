"""
AI Provider 测试：错误处理、重试机制、超时控制（使用 mock，不需要真实 API）
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from ai.providers.openai_provider import OpenAIProvider


class TestOpenAIProviderRetry:
    """测试 OpenAI Provider 的重试机制。"""

    def test_provider_init(self):
        """Provider 正确初始化。"""
        provider = OpenAIProvider(
            api_key="test-key",
            base_url="https://api.test.com/v1",
            model="test-model",
        )
        assert provider.name == "openai"
        assert provider.model == "test-model"
        assert provider.max_retries == 3
        assert provider.timeout == 60.0

    def test_provider_custom_retry_config(self):
        """Provider 支持自定义重试次数和超时。"""
        provider = OpenAIProvider(
            api_key="test-key",
            max_retries=5,
            timeout=30.0,
        )
        assert provider.max_retries == 5
        assert provider.timeout == 30.0

    def test_deepseek_provider_uses_defaults(self):
        """DeepSeek Provider 使用默认配置。"""
        from ai.providers.deepseek_provider import DeepSeekProvider
        provider = DeepSeekProvider(api_key="test-key")
        assert provider.name == "deepseek"
        assert "deepseek" in provider.base_url

    def test_custom_provider_requires_base_url(self):
        """Custom Provider 必须提供 base_url。"""
        from ai.providers.custom_provider import CustomProvider
        with pytest.raises(ValueError, match="base_url"):
            CustomProvider(api_key="test-key", model="test-model")

    def test_custom_provider_requires_model(self):
        """Custom Provider 必须提供 model。"""
        from ai.providers.custom_provider import CustomProvider
        with pytest.raises(ValueError, match="model"):
            CustomProvider(api_key="test-key", base_url="https://test.com/v1")

    def test_available_providers(self):
        """注册的 Provider 列表完整。"""
        from ai.manager import available_providers
        providers = available_providers()
        assert "openai" in providers
        assert "deepseek" in providers
        assert "custom" in providers

    def test_create_unknown_provider_raises(self):
        """创建未知 Provider 应抛出 ValueError。"""
        from ai.manager import create_provider
        with pytest.raises(ValueError, match="Unknown AI provider"):
            create_provider("nonexistent", "key")


class TestAIProviderInterface:
    """测试 AI Provider 接口一致性。"""

    def test_all_providers_implement_analyze(self):
        """所有 Provider 必须实现 analyze 方法。"""
        from ai.providers.openai_provider import OpenAIProvider
        from ai.providers.deepseek_provider import DeepSeekProvider
        from ai.providers.custom_provider import CustomProvider
        for cls in [OpenAIProvider, DeepSeekProvider, CustomProvider]:
            assert hasattr(cls, 'analyze'), f"{cls.__name__} 缺少 analyze 方法"

    def test_all_providers_implement_proofread(self):
        """所有 Provider 必须实现 proofread 方法。"""
        from ai.providers.openai_provider import OpenAIProvider
        from ai.providers.deepseek_provider import DeepSeekProvider
        from ai.providers.custom_provider import CustomProvider
        for cls in [OpenAIProvider, DeepSeekProvider, CustomProvider]:
            assert hasattr(cls, 'proofread'), f"{cls.__name__} 缺少 proofread 方法"

    def test_all_providers_implement_rewrite(self):
        """所有 Provider 必须实现 rewrite 方法。"""
        from ai.providers.openai_provider import OpenAIProvider
        from ai.providers.deepseek_provider import DeepSeekProvider
        from ai.providers.custom_provider import CustomProvider
        for cls in [OpenAIProvider, DeepSeekProvider, CustomProvider]:
            assert hasattr(cls, 'rewrite'), f"{cls.__name__} 缺少 rewrite 方法"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])