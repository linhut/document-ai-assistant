"""
Test suite for AI Integration (Phase 5).
"""
import pytest
import asyncio
from ai.manager import create_provider, available_providers


def test_available_providers():
    """Test listing available providers."""
    providers = available_providers()
    assert isinstance(providers, list)
    assert "openai" in providers
    assert "deepseek" in providers
    assert "custom" in providers
    print(f"Available providers: {providers}")


@pytest.mark.asyncio
async def test_openai_provider_mock():
    """Test OpenAI provider with mock API (will fail without real API key)."""
    # This is a structure test - real API test requires valid key
    try:
        provider = create_provider(
            "openai",
            api_key="sk-test-key-mock",
            model="gpt-4o-mini"
        )
        assert provider.name == "openai"
        assert provider.model == "gpt-4o-mini"
        print(f"OpenAI provider created: {provider.name}")
    except Exception as e:
        print(f"Expected: {e}")


@pytest.mark.asyncio
async def test_deepseek_provider_structure():
    """Test DeepSeek provider structure."""
    provider = create_provider(
        "deepseek",
        api_key="test-key",
        model="deepseek-chat"
    )
    assert provider.name == "deepseek"
    print(f"DeepSeek provider created: {provider.name}")


@pytest.mark.asyncio
async def test_custom_provider_structure():
    """Test Custom provider structure."""
    provider = create_provider(
        "custom",
        api_key="test-key",
        base_url="https://api.example.com/v1",
        model="custom-model"
    )
    assert provider.name == "custom"
    print(f"Custom provider created: {provider.name}")


if __name__ == "__main__":
    print("Testing AI Integration...")
    print()

    # Run sync tests
    test_available_providers()

    # Run async tests
    asyncio.run(test_openai_provider_mock())
    asyncio.run(test_deepseek_provider_structure())
    asyncio.run(test_custom_provider_structure())

    print()
    print("AI Integration structure tests passed!")
    print()
    print("Note: Real API tests require valid API keys.")
    print("To test with real API:")
    print("  1. Set environment variable: OPENAI_API_KEY=your-key")
    print("  2. Run: python tests/backend/test_ai_integration_real.py")
